"""
Command interface / API for GBA emulator

See lua\\socketserver.lua for the server implementation
"""
import socket
import time
import typing as T


class CommandClient:

    def __init__(self, host: str, port: int) -> None:
        self.sleep_duration = 20
        self._host = host
        self._port = port
        self._connected = False
        self._socket: socket.socket = None
        self._connect()

    def _connect(self) -> T.Optional[T.NoReturn]:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host, self._port))
        self._socket.settimeout(1.0)  # localhost
        self._connected = True

    def _disconnect(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self._connected = False

    def reset(self) -> None:
        """
        Disconnect and reconnect
        """
        self._disconnect()
        self._connect()

    def do_button_command(self, cmd: bytes) -> None:
        try:
            self._socket.send(cmd)
            self._socket.recv(128)
        except TimeoutError:
            print("Timed out on socket read in button command")
        finally:
            self._socket.send(b"clear")  # best effort here
            self._socket.recv(128)

    def do_data_command(self, cmd: bytes) -> bytes:
        """
        Issue a command that expects a response
        """
        self._socket.send(cmd)
        try:
            resp = self._socket.recv(16384)  # TODO: maybe this buffer is too large?
            return resp
        except TimeoutError:
            print("Timed out on socket read")
            return b" " * 8192

    def dispatch(self, cmd: str) -> T.Optional[bytes]:
        """
        If the command is a button command, reset keys after issuing the command.
        """
        if self._socket is None:
            self.reset()

        if cmd in ["A", "B", "U", "R", "L", "D", "start", "select"]:
            fmtcmd = bytes(f"B:{cmd}", 'utf-8')
            return self.do_button_command(fmtcmd)

        fmtcmd = bytes(cmd, "utf-8")
        return self.do_data_command(fmtcmd)


if __name__ == "__main__":
    # run in REPL mode
    client = CommandClient('localhost', 10018)
    while True:
        try:
            response = client.dispatch(input("Command: "))
            if response is not None:
                print(response)
        except KeyboardInterrupt:
            print("Exiting REPL")
            break
        except socket.error:
            client.reset()  # if this fails just exit REPL
        finally:
            client._disconnect()
