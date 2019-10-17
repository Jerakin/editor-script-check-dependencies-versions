#!/usr/bin/env python3
"""
Editor script to create a component for the provided resource
"""

from pathlib import Path
import json
from urllib.request import urlopen
from urllib.request import Request
import configparser
import re
from packaging import version
import time


def get_dependencies(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['project']['dependencies'].split(",")


def get_header():
    root = Path().cwd()
    config_file = root / ".editor-script-settings" / "editor-script-check-dependencies"
    header = {"User-Agent": "editor-script-check-dependencies"}
    if config_file.exists():
        config = configparser.ConfigParser()
        config.read(config_file)
        if config.has_section("Authenticate"):
            if "token" in config["Authenticate"]:
                header['Authorization'] = "token " + config['Authenticate']['TOKEN']
    return header


def have_releases(request):
    """Check if a repository is using releases
    GET /repos/:owner/:repo/releases"""
    with urlopen(request) as response:
        if response.status not in [200, 304]:
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
    with urlopen(request) as response:
        if response.status not in [200, 304]:
            return

        response_content = response.read()
        response_content.decode('utf-8')
        json_response = json.loads(response_content)

        version_string = json_response["tag_name"]
        return version.parse(version_string)


def compare_versions(old, new, project, url):
    """Print our version information"""
    if new > old:
        print("Project '{}' is out dated, latest version is".format(project))
        print("  {}/archive/{}.zip\n".format(url, new))
    else:
        print("Project '{}' is up to date.\n".format(project))


def get_latest_tags(request):
    """If a project is not using releases presume the latest tag is the latest release
    GET /repos/:owner/:repo/tags"""
    with urlopen(request) as response:
        if response.status not in [200, 304]:
            return

        response_content = response.read()
        response_content.decode('utf-8')
        json_response = json.loads(response_content)
        tags = []
        for p in json_response:
            tags.append(p["name"])
        tags.sort(key=version.parse)
        return version.parse(tags[-1])


def check_rate_limit(header, dependencies):
    """Github rate limits the API calls, this checks if we are and prints some info
    GET /rate_limit"""

    request_url = "https://api.github.com/rate_limit"
    request = Request(request_url, headers=header)
    with urlopen(request) as response:
        if response.status not in [200, 304]:
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
    game_project = Path().cwd() / "game.project"
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
        current_version = version.parse(dependency.split("/")[-1].replace(".zip", ""))
        if current_version.epoch == -1:
            print("{} does not follow Semantic Versioning.".format(project))

        # First check of there are any releases
        releases = "https://api.github.com/repos/{}/{}/releases".format(owner, project)
        request = Request(releases, headers=header)
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


if __name__ == '__main__':
    main()
