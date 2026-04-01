from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

PORT = 8000

items = []

class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/items":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(items).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/items":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            item = {
                "id": len(items) + 1,
                "name": data.get("name"),
                "type": data.get("type"),
                "description": data.get("description")
            }

            items.append(item)

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(item).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def do_DELETE(self):
        if self.path.startswith("/items/"):
            try:
                item_id = int(self.path.split("/")[-1])

                for i, item in enumerate(items):
                    if item["id"] == item_id:
                        del items[i]
                        break

                print("Updated items:", items)  # debug

                self.send_response(200)
                self.end_headers()

            except Exception as e:
                print("DELETE ERROR:", e)
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"Serving website at http://localhost:{PORT}")
    server = HTTPServer(("localhost", PORT), Handler)
    server.serve_forever()