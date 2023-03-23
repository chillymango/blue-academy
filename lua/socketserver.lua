--- Original Source: https://github.com/mgba-emu/mgba/blob/master/res/scripts/socketserver.lua
--- TODO: the server is unhappy when we have a socket disconnect. we're hacking around it for now
---     but i suspect we'll run into problems when we try to run learning at 10x speed

lastkeys = nil
server = nil
ST_sockets = {}
nextID = 1

local KEY_NAMES = { "A", "B", "s", "S", "<", ">", "^", "v", "R", "L" }

function ST_stop(id)
	local sock = ST_sockets[id]
	ST_sockets[id] = nil
	sock:close()
end

function ST_format(id, msg, isError)
	local prefix = "Socket " .. id
	if isError then
		prefix = prefix .. " Error: "
	else
		prefix = prefix .. " Received: "
	end
	return prefix .. msg
end

function ST_error(id, err)
	console:error(ST_format(id, err, true))
	ST_stop(id)
end

function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			console:log(ST_format(id, p:match("^(.-)%s*$")))
			if p:sub(1, 2) == "B:" then
				buttons = p:sub(3)
				if buttons:find("U") then
					emu:addKey(C.GBA_KEY.UP)
                elseif buttons:find("R") then
					emu:addKey(C.GBA_KEY.RIGHT)
                elseif buttons:find("L") then
					emu:addKey(C.GBA_KEY.LEFT)
                elseif buttons:find("D") then
					emu:addKey(C.GBA_KEY.DOWN)
                elseif buttons:find("A") then
					emu:addKey(C.GBA_KEY.A)
                elseif buttons:find("B") then
					emu:addKey(C.GBA_KEY.B)
                elseif buttons == "start" then
					emu:addKey(C.GBA_KEY.START)
                    console:log("Start")
                elseif buttons == "select" then
					emu:addKey(C.GBA_KEY.SELECT)
                else
                    console:log("Warning: don't recognize input")
				end
				untilKeyReset = 2
            elseif p == "checksum" then
                sock.send(emu:checksum())
			elseif p == "screenshot" then
				emu:screenshot("current.png")
            elseif p == "test" then
            else
                console.log("Resetting keys")
                emu:setKeys(0)
            end
		else
--			if err ~= socket.ERRORS.AGAIN then
--				console:error(ST_format(id, err, true))
--				ST_stop(id)
--			end
			return
		end
	end
end

function ST_scankeys()
	local keys = emu:getKeys()
	if keys ~= lastkeys then
		lastkeys = keys
		local msg = "["
		for i, k in ipairs(KEY_NAMES) do
			if (keys & (1 << (i - 1))) == 0 then
				msg = msg .. " "
			else
				msg = msg .. k;
			end
		end
		msg = msg .. "]\n"
		for id, sock in pairs(ST_sockets) do
			if sock then sock:send(msg) end
		end
	end
end

function ST_accept()
	local sock, err = server:accept()
	if err then
		console:error(ST_format("Accept", err, true))
		return
	end
	local id = nextID
	nextID = id + 1
	ST_sockets[id] = sock
	sock:add("received", function() ST_received(id) end)
	sock:add("error", function() ST_error(id) end)
	console:log(ST_format(id, "Connected"))
end

function resetKeys()
	if untilKeyReset >= 0 then
		untilKeyReset = untilKeyReset - 1
	end
	if untilKeyReset == 0 then
		emu:setKeys(0)
	end
end

callbacks:add("frame", resetKeys)

local port = 10018
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			port = port + 1
		else
			console:error(ST_format("Bind", err, true))
			break
		end
	else
		local ok
		ok, err = server:listen()
		if err then
			server:close()
			console:error(ST_format("Listen", err, true))
		else
			console:log("Socket Server Test: Listening on port " .. port)
			server:add("received", ST_accept)
		end
	end
end
