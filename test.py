print ("I forgot how to code in python")
print("But I will learn it again!")
print("Practice makes perfect.")
print("Let's start coding!")

print("Sam_testing")

from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8000

class Handler(SimpleHTTPRequestHandler):
    pass

if __name__ == "__main__":
    print(f"Serving website at http://localhost:{PORT}")
    server = HTTPServer(("localhost", PORT), Handler)
    server.serve_forever()
