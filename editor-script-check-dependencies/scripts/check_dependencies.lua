-- THIS SCRIPT IS ONLY A WORK IN PROGRESS, I PAUSED THE PROGRESS BECAUSE HTTP ISN'T SUPPORTED IN EDITOR SCRIPTS
-- ONLY KEEPING THIS SCRIPT HERE IF I CAN FIND A WAY TO USE HTTP

local lip = require "editor-script-check-dependencies.scripts.LIP"
local semver = require "editor-script-check-dependencies.scripts.semver"

local HEADER =  {["User-Agent"] = "editor-script-check-dependencies"}

local M = {}

function mysplit (inputstr, sep)
	if sep == nil then
		sep = "%s"
	end
	local t={}
	for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
		table.insert(t, str)
	end
	return t
end


local function get_libraries()
	local game_project = lip.load("game.project")
	return game_project.project.dependencies
end


local function http_result_check_new(self, _, response, url, project, current_version)
	if response.status == 200 or response.status == 304 then
		local response_as_json = json.decode(response.response)
		local version_string = response_as_json.tag_name
		local new_version = semver(version_string)
		if new_version ~= nil then
			if new_version > current_version then
				print("Project '" .. project .. "' outdated, latest version is")
				print("  " .. url .. "/archive/" .. version_string .. ".zip")
			end
		end
	end
end

local function http_result_latest(self, _, response, url, project)
	if response.status == 200 or response.status == 304 then
		local response_as_json = json.decode(response.response)
		local version_string = response_as_json.tag_name
		print("Found library pointing to master it's recommended to use a locked down version")
		print("  " .. url .. "/archive/" .. version_string .. ".zip")
	end
end

function M.main()
	local libs = get_libraries()
	for w in libs:gmatch("([^,]+)") do
		local url = w:gsub("/archive/.*", "")

		local _url_split = {}
		for seg in url:gmatch("([^/]+)") do
			table.insert(url_split, seg)
		end
		local project = _url_split[#_url_split]
		local owner = _url_split[#_url_split-1]

		local request_url = "https://api.github.com/repos/" ..owner .."/" .. project .. "/releases/latest"

		if string.find(w, "master.zip") then
			http.request(request_url, "GET", function(self, _, res) http_result_latest(self, _, res, url, project) end, HEADER)
		else
			local current_version = semver(w:gsub(".*/archive/", ""))
			if current_version == nil then
				print("Current version does not follow Semantic Versioning.")
			else
				http.request(request_url, "GET", function(self, _, res) http_result_check_new(self, _, res, url, project, current_version) end, HEADER)
			end
		end
	end
end

return M