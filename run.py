from app import create_app
import os
import socket

app = create_app()


def _find_available_port(start_port: int) -> int:
    port = start_port
    while port < start_port + 20:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start_port

if __name__ == '__main__':
    requested_port = int(os.getenv("PORT", 5000))
    port = _find_available_port(requested_port)
    if port != requested_port:
        print(f"⚠️ Port {requested_port} is busy, using {port} instead")
    app.run(debug=True, port=port, use_reloader=False)