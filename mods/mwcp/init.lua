local function run_command(name, args, sudo)
	if args == "" then
		return false, "You need a command."
	end
	local found, _, commandname, params = args:find("^([^%s]+)%s(.+)$")
	if not found then
		commandname = args
	end
	local command = minetest.chatcommands[commandname]
	if not command then
		return false, "Not a valid command."
	end
	if not sudo and not minetest.check_player_privs(name, command.privs) then
		return false, "Your privileges are insufficient."
	end
	minetest.log("action", name.."@WebPanel runs "..args)
	return command.func(name, (params or ""))
end

local function process_frompanel(data)
	for i = 1, #data do
		local item = data[i]
		print("Recieved mode " .. item.mode .. " from webpanel.")

		if item.mode == "chat_or_cmd" then
			if item.content:sub(1, 1) == "/" then
				run_command(item.username, item.content:sub(2))
			else
				minetest.chat_send_all("<" .. item.username .. "@WebPanel> " .. item.content)
			end
		elseif item.mode == "cmd" then
			if item.content:sub(1, 1) == "/" then
				run_command(item.username, item.content:sub(2))
			else
				run_command(item.username, item.content)
			end
		elseif item.mode == "cmd_sudo" then
			if item.content:sub(1, 1) == "/" then
				run_command(item.username, item.content:sub(2), true)
			else
				run_command(item.username, item.content, true)
			end
		end
	end
end

local mech = dofile(minetest.get_modpath("mwcp") .. "/http.lua")
local sync_interval = nil
local function init()
	-- Get startup data from webpanel
	local f = io.open(minetest.get_worldpath() .. "/webpanel.txt", "r")
	local data = minetest.deserialize(f:read("*all"))
	f:close()
	sync_interval = data.sync_interval
	mech.init(process_frompanel, data)
end
init()

local function handle_chat(name, message)
	local chat = {type = "chat", name = name, message = message}
	mech.send(chat)
end

local function updatetick()
	mech.sync()
	minetest.after(sync_interval, updatetick)
end
minetest.after(sync_interval, updatetick)
minetest.register_on_chat_message(handle_chat)
