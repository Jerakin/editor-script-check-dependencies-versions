#!/usr/bin/env python3
"""
Editor script to create a component for the provided resource
"""

import os
import json
try:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.request import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import HTTPError

try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    from configparser import ConfigParser

import re
from distutils.version import StrictVersion
import time


def MyStrictVersion(v):
    m = re.search('^(\D|)+(.*)', v)
    if m:
        v = m.group(2)
    v = v or "0.0"
    return StrictVersion(v)


def get_dependencies(config_file):
    config = ConfigParser()
    config.read(config_file)
    if config.has_option("project", "dependencies"):
        return config.get('project', 'dependencies').split(",")
    return []


def get_header():
    config_file = os.path.join(os.getcwd(),".editor-script-settings", "editor-script-check-dependencies")
    header = {"User-Agent": "editor-script-check-dependencies"}
    if os.path.exists(config_file):
        config = ConfigParser()
        config.read(config_file)
        if config.has_option("Authenticate", "TOKEN"):
            header['Authorization'] = "token " + config.get('Authenticate', 'TOKEN')
    return header


def have_releases(request):
    """Check if a repository is using releases
    GET /repos/:owner/:repo/releases"""
    response = urlopen(request)
    if response.getcode() not in [200, 304]:
        return False
    response_content = response.read()
    response_content.decode('utf-8')
    json_response = json.loads(response_content)
    if json_response:
        return True
    return False


def get_latest_version(request):
    """Get the latest version
    GET /repos/:owner/:repo/releases/latest"""
    response = urlopen(request)
    if response.getcode() not in [200, 304]:
        return

    response_content = response.read()
    response_content.decode('utf-8')
    json_response = json.loads(response_content)

    version_string = json_response["tag_name"]
    try:
        return MyStrictVersion(version_string)
    except ValueError:
        return MyStrictVersion("0.0")


def compare_versions(old, new, project, url):
    """Print our version information"""
    if new > old:
        print("Project '{}' is outdated, latest version is".format(project))
        print("  {}/archive/{}.zip\n".format(url, new))
    else:
        if old == MyStrictVersion("0.0"):
            print("Project '{}' does not have any versions.\n".format(project))
        else:
            print("Project '{}' is up to date.\n".format(project))


def get_latest_tags(request):
    """If a project is not using releases presume the latest tag is the latest release
    GET /repos/:owner/:repo/tags"""
    response = urlopen(request)
    if response.getcode() not in [200, 304]:
        return

    response_content = response.read()
    response_content.decode('utf-8')
    json_response = json.loads(response_content)
    tags = []
    for p in json_response:
        tags.append(p["name"])
    try:
        tags.sort(key=MyStrictVersion)
        if tags:
            return MyStrictVersion(tags[-1])
        else:
            return MyStrictVersion("0.0")
    except ValueError:
        return MyStrictVersion("0.0")


def check_rate_limit(header, dependencies):
    """Github rate limits the API calls, this checks if we are and prints some info
    GET /rate_limit"""

    request_url = "https://api.github.com/rate_limit"
    request = Request(request_url, headers=header)
    response = urlopen(request)
    if response.getcode() not in [200, 304]:
        return
    response_content = response.read()
    response_content.decode('utf-8')
    json_response = json.loads(response_content)

    limit = json_response["resources"]["core"]["limit"]
    remaining = json_response["resources"]["core"]["remaining"]
    reset = json_response["resources"]["core"]["reset"]

    if len(dependencies) > remaining:
        if "token" not in header:
            print("You are rate limited to {} dependency checks, add a 'token' to increase this limit".format(limit))
        print("You are rate limited until", time.ctime(reset))
    if remaining == 0:
        return True


def main():
    game_project = os.path.join(os.getcwd(), "game.project")
    header = get_header()
    dependencies = get_dependencies(game_project)

    if check_rate_limit(header, dependencies):
        # No need to continue if we are rate-limited
        return

    for dependency in dependencies:
        url = re.match("(.*)\/archive", dependency)
        if not url:
            continue
        url = url.group(1)
        project = url.split("/")[-1]
        owner = url.split("/")[-2]

        # Collect the version from the url
        try:
            current_version = MyStrictVersion(dependency.split("/")[-1].replace(".zip", ""))
        except ValueError:
            if "master.zip" in dependency:
                print("Project '{}' is using master this is not recommended.".format(project))
            else:
                print("Project '{}' does not follow Semantic Versioning.".format(project))
            current_version = MyStrictVersion("0.0")

        # First check of there are any releases
        releases = "https://api.github.com/repos/{}/{}/releases".format(owner, project)
        request = Request(releases, headers=header)
        try:
            if have_releases(request):
                latest = "https://api.github.com/repos/{}/{}/releases/latest".format(owner, project)
                request = Request(latest, headers=header)
                latest = get_latest_version(request)
            else:
                # Get the latest version from tags if there are no releases
                releases = "https://api.github.com/repos/{}/{}/tags".format(owner, project)
                request = Request(releases, headers=header)
                latest = get_latest_tags(request)

            compare_versions(current_version, latest, project, url)

            if "Authorization" not in header:
                time.sleep(2)  # We are only allowed to do one call every 2 min if we are not using authorization
        except HTTPError as e:
            print("Project '{}' could not be checked, HTTPError {}.".format(project, e.code))


if __name__ == '__main__':
    main()
