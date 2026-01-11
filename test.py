from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8000

class Handler(SimpleHTTPRequestHandler):
    pass

if __name__ == "__main__":
    print(f"Serving website at http://localhost:{PORT}")
    server = HTTPServer(("localhost", PORT), Handler)
    server.serve_forever()
