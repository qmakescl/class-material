import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SITE_DIRECTORY = Path(__file__).parent / "docs"


def main() -> None:
    """Serve the static class materials for local preview."""
    parser = argparse.ArgumentParser(description="Preview the class materials site")
    parser.add_argument("--host", default="127.0.0.1", help="address to bind")
    parser.add_argument("--port", default=8000, type=int, help="port to listen on")
    args = parser.parse_args()

    handler = partial(SimpleHTTPRequestHandler, directory=SITE_DIRECTORY)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving {SITE_DIRECTORY} at http://{args.host}:{args.port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
