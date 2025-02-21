-- THIS SCRIPT IS ONLY A WORK IN PROGRESS, I PAUSED THE PROGRESS BECAUSE HTTP ISN'T SUPPORTED IN EDITOR SCRIPTS
-- ONLY KEEPING THIS SCRIPT HERE IF I CAN FIND A WAY TO USE HTTP

local lip = require "editor-script-check-dependencies.scripts.LIP"
local semver = require "editor-script-check-dependencies.scripts.semver"

local M = {}

local ok = "✔"
local error = "✖"
local warning = "!"

local function get_libraries()
	local libraries = {}
	local i = 0
	local game_project = lip.load("game.project")
	
	while true do
		local dep_url = game_project.project["dependencies#" .. i]
		if dep_url == nil then
			break
		end
		table.insert(libraries, dep_url)
		i = i +1
	end
	return libraries
end


local function format_result(result_table)
	local entries = {}
	for _, dependency in pairs(result_table) do
		local entry = {
			name=dependency.owner .. "/" .. dependency.project .. " (" .. dependency.current .. ")",
			latest=dependency.latest_url,
		}
		local current = dependency.current ~= nil and semver(dependency.current:gsub("[v]+", "")) or nil
		local latest = dependency.latest ~= nil and semver(dependency.latest:gsub("[v]+", "")) or nil
		if current == nil then
			entry.prefix = warning
		else
			if latest == nil then
				entry.prefix = ok
				entry.latest = "No remote version found."
			elseif current >= latest then
				entry.prefix = ok
				entry.latest = nil
			else
				entry.prefix = error
			end
		end
		table.insert(entries, entry)
	end
	return entries
end

local function print_result(result_table)
	print()
	print("editor-script-check-depedendencies")
	print(" " .. ok      .. "  The dependency is up to date.")
	print(" " .. error   .. "  The dependency is outdated.")
	print(" " .. warning .. "  The dependency is not using a semver supported release.")
	print()
	print()
	local formatted = format_result(result_table)
	for _, entry in pairs(formatted) do
		print(entry.prefix .. " " .. entry.name)
		if entry.latest then
			print("    " .. entry.latest)
		end
		print()
	end
end

local function get_github_header()
	local header = {["User-Agent"] = "editor-script-check-dependencies"}
	local config_file = ".editor-script-settings/editor-script-check-dependencies"
	local file_attrib = editor.external_file_attributes(config_file)
	if file_attrib.exists then
		local config = lip.load(file_attrib.path)
		local token = config.Authenticate.github_token
		if token then
			header['Authorization'] = "token " .. token
		end
	end
	return header
end

local function github_standard(url, result_table)
	local owner, project, version = url:match("[%w]*://github%.com/([%w-]*)/([%w-]*)[%w/.]*/([%w%._]*).zip")
	if owner == nil or project == nil or version == nil then
		return false
	end

	local headers = get_github_header()
	local request_url = "https://api.github.com/repos/" ..owner .."/" .. project .. "/releases/latest"
	local response = http.request(request_url, {method="GET", as="json", headers=headers})
	
	local latest_url, tag_name
	if response.status == 200 then
		tag_name = response["body"]["tag_name"]
		if tag_name then
			latest_url = "https://github.com/" .. owner .. "/" .. project .. "/archive/" .. tag_name .. ".zip"
		else
			latest_url = "No remote versions found"
		end
	elseif response.status == 404 then
		request_url = "https://api.github.com/repos/" ..owner .."/" .. project .. "/tags"
		response = http.request(request_url, {method="GET", as="json", headers=headers})
		if response.status == 200 then
			if response.body[1] ~= nil then
				tag_name = response.body[1].name
				latest_url = "https://github.com/" .. owner .. "/" .. project .. "/archive/" .. tag_name .. ".zip"
			end
		end
	end

	table.insert(result_table, {
		owner=owner,
		project=project,
		current_url=url,
		latest_url=latest_url,
		current=version,
		latest=tag_name,
	})
end

function M.main()
	local libs = get_libraries()
	local result_table = {}

	for _, w in pairs(libs) do
		local response = github_standard(w, result_table)
		if response == false then
			print("Url pattern or host not supported: " .. w)
		end
	end
	print_result(result_table)
end

return M