"""
Command interface / API for GBA emulator

See lua\\socketserver.lua for the server implementation
"""
import socket
import time
import typing as T


class CommandClient:

    def __init__(self, host: str, port: int) -> None:
        self.sleep_duration = 10
        self._host = host
        self._port = port
        self._connected = False
        self._socket: socket.socket = None
        self._connect()

    def _connect(self) -> T.Optional[T.NoReturn]:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host, self._port))
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

    def dispatch(self, cmd: str) -> None:
        """
        If the command is a button command, reset keys after issuing the command.
        """
        if self._socket is None:
            self.reset()

        if cmd in ["A", "B", "U", "R", "L", "D", "start", "select"]:
            fmtcmd = f"B:{cmd}"
        else:
            fmtcmd = cmd
        fmtcmd = bytes(fmtcmd, "utf-8")
        self._socket.send(fmtcmd)

        time.sleep(self.sleep_duration / 1E3)

        self._socket.send(b"clear")


if __name__ == "__main__":
    # run in REPL mode
    client = CommandClient('localhost', 10018)
    while True:
        try:
            client.dispatch(input("Command: "))
        except KeyboardInterrupt:
            print("Exiting REPL")
            break
        except socket.error:
            client.reset()  # if this fails just exit REPL
        finally:
            client._disconnect()
