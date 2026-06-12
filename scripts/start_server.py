"""Find a free port and start the GenAI Integration Hub API."""

import socket
import subprocess
import sys

DEFAULT_PORT = 8000
HOST = "0.0.0.0"


def find_free_port(start: int = DEFAULT_PORT, host: str = HOST) -> int:
    port = start
    while port <= 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                return port
            except OSError:
                port += 1
    raise SystemExit(f"No free port found starting at {start}")


def main() -> None:
    port = find_free_port()
    if port != DEFAULT_PORT:
        print(f"Port {DEFAULT_PORT} is in use, using {port} instead.")
    print(f"API docs: http://localhost:{port}/docs")
    print("Press Ctrl+C to stop.\n")
    raise SystemExit(
        subprocess.call(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "genai_hub.main:app",
                "--reload",
                "--host",
                HOST,
                "--port",
                str(port),
            ]
        )
    )


if __name__ == "__main__":
    main()
