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

function readRam(mem_name)
    for name, mem in pairs(emu.memory) do
        if name == mem_name then
            base = mem:base()
            length = mem:bound() - mem:base()
            msg = "Reading " .. mem_name .. " from " .. tostring(base) .. " len " .. tostring(length)
			if length > 4096 then
				section_1 = mem:readRange(base, length / 2)
				section_2 = mem:readRange(base + length / 2, length / 2)
				output = section_1 .. section_2
			else
				output = mem:readRange(base, length)
			end
            console:log(msg)
            return output
        end
    end
    console:error("Could not find %s", mem_name)
end

function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			if p:sub(1, 2) == "B:" then
				buttons = p:sub(3)
				if buttons:find("U") then
					emu:addKey(C.GBA_KEY.UP)
					sock:send("OK")
                elseif buttons:find("R") then
					emu:addKey(C.GBA_KEY.RIGHT)
					sock:send("OK")
                elseif buttons:find("L") then
					emu:addKey(C.GBA_KEY.LEFT)
					sock:send("OK")
                elseif buttons:find("D") then
					emu:addKey(C.GBA_KEY.DOWN)
					sock:send("OK")
                elseif buttons:find("A") then
					emu:addKey(C.GBA_KEY.A)
					sock:send("OK")
                elseif buttons:find("B") then
					emu:addKey(C.GBA_KEY.B)
					sock:send("OK")
                elseif buttons == "start" then
					emu:addKey(C.GBA_KEY.START)
					sock:send("OK")
                elseif buttons == "select" then
					emu:addKey(C.GBA_KEY.SELECT)
					sock:send("OK")
                else
                    console:log("Warning: don't recognize input")
					sock:send("NOT OK")
				end
				untilKeyReset = 2
            elseif p == "checksum" then
                sock:send(emu:checksum())
			elseif p == "screenshot" then
				emu:screenshot("current.png")
				sock:send("OK")
            elseif p == "dump_wram" then
				-- NOTE: reading wram normally seems to be broken :(
				result = emu:readRange(49152, 8192)
                sock:send(result)
            elseif p == "dump_hram" then
                result = readRam("hram")
                sock:send(result)
            elseif p == "dump_sram" then
                result = readRam("sram")
                sock:send(result)
            elseif p == "dump_vram" then
                result = readRam("vram")
                sock:send(result)
			elseif p == "fasttext" then
				emu:write8(54101, 0)
				sock:send('OK')
			elseif p == "memtest" then
				result = emu:readRange(53248, 4096)
				sock:send(result)
            elseif p == "test" then
                console:log("test")
            else
                emu:setKeys(0)
				sock:send("OK")
            end
		else
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
		emu:write8(54101, 0)
	end
end

function setSpeed()
	emu:write8()
end

callbacks:add("frame", resetKeys)
callbacks:add("frame", setSpeed)

local port = 10018
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			port = port + 100
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
