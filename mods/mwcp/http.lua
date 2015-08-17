local function warning(msg)
	print("[WARNING] " .. msg)
end

local process_frompanel = nil
local http          = nil
local ltn12         = nil
local sync_timeout  = nil
local server_id     = nil
local auth_key      = nil
local webpanel_host = nil
local sync_interval = nil
local function init(iprocess_frompanel, data)
	process_frompanel = iprocess_frompanel
	sync_timeout  = data.sync_timeout
	server_id     = data.server_id
	auth_key      = data.auth_key
	webpanel_host = data.webpanel_host
	sync_interval = data.sync_interval

	-- Include modules
	local ie = _G
	if minetest.request_insecure_environment then
		ie = minetest.request_insecure_environment()
		if not ie then
			error("Insecure environment required!")
		end
	end

	http  = ie.require("socket.http")
	ltn12 = ie.require("ltn12")
	http.TIMEOUT = sync_timeout
end

local function validate_response(code, resp)
	if code ~= 200 then
		if code == 404 then
			warning("The webpanel reports that this server does not exist!")
		else
			warning("The webpanel gave an unknown HTTP response code! (" .. code .. ")")
		end
		return false
	end

	if resp == "auth" then
		warning("Authentication error when requesting commands from webpanel")
		return false
	end

	if resp == "offline" then
		warning("The webpanel reports that this server should be offline!")
		return false
	end

	return true
end

local function validate_response_post(code, resp)
	if resp and resp[1] then
		resp = resp[1]:trim()
	else
		return false
	end

	if not validate_response(code, resp) then
		return false
	end

	if string.find(resp, "return", 1) == nil then
		warning("The webpanel gave an invalid response!")
		print(dump(resp))
		return false
	end

	return true
end

local function validate_response_json(code, resp)
	if resp and resp[1] then
		resp = resp[1]:trim()
	else
		return false
	end

	if not validate_response(code, resp) then
		return false
	end

	if string.find(resp, "return", 1) == nil then
		warning("The webpanel gave an invalid response!")
		print(dump(resp))
		return false
	end

	return true
end

local function sync()
	local host   = webpanel_host .. "/"
	local method = "GET"
	local path   = "api/" .. auth_key .. "/" .. server_id .. "/server_update/"
	local params = ""
	local resp   = {}

	-- Compose URL
	local url = ""
	if params:trim() ~= "" then
		url = host .. path .. "?" .. params
	else
		url = host .. path
	end

	-- Make Request
	local client, code, headers, status = http.request({url=url, sink=ltn12.sink.table(resp),
			method=method })
	-- Not used:
	-- headers=args.headers, source=args.source,
	-- step=args.step, proxy=args.proxy, redirect=args.redirect, create=args.create

	if validate_response_json(code, resp) then
		resp = resp[1]:trim()
		process_frompanel(minetest.deserialize(resp))
	end
end

local function send(data)
	local host   = webpanel_host .. "/"
	local method = "POST"
	local path   = "api/" .. auth_key .. "/" .. server_id .. "/server_update/"
	local resp   = {}
	local url = host .. path
	local headers = {}
	headers['Content-Length'] = #'data=' + #data
	headers['Content-Type'] = 'application/x-www-form-urlencoded'
	local sink = ltn12.sink.table(resp)
	local source = ltn12.source.string('data=' .. data)

	local client, code, headers, status = http.request({url=url, sink=sink, source=source,
	 	method=method, headers=headers})

	validate_response_post(code, resp)
end

return {
	init = init,
	sync = sync,
	send = send
}
