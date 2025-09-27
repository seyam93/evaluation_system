#!/usr/bin/env python3
"""
Simple HTTP server to test the HTML templates locally
Run this script and open http://localhost:8000 in your browser
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Change to the project directory
os.chdir('/Users/seyam/Development/myproject')

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Redirect root to candidate list
        if self.path == '/':
            self.path = '/templates/students/candidate_list.html'
        return super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print("\nAvailable pages:")
        print(f"  Candidate List: http://localhost:{PORT}/templates/students/candidate_list.html")
        print(f"  Add Candidate:  http://localhost:{PORT}/templates/students/candidate_form.html")
        print(f"  Candidate Detail: http://localhost:{PORT}/templates/students/candidate_detail.html")
        print(f"\nPress Ctrl+C to stop the server")

        # Automatically open browser
        webbrowser.open(f'http://localhost:{PORT}/templates/students/candidate_list.html')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")