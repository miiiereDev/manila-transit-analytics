# Manila Transit Analytics - Main GUI Dashboard Runner
import http.server
import socketserver
import webbrowser
import threading
import os
import sys

# Define port
PORT = 8000

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to disable caching and allow seamless UI refreshes."""
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_server():
    """Starts the HTTP server on a separate thread."""
    # Use standard TCPServer with reuse_address enabled
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
            print(f"\n[SERVER] Web server successfully running on http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"\n[ERROR] Failed to start local server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("        MANILA TRANSIT ANALYTICS - COMPANION DASHBOARD")
    print("=" * 60)
    
    # 1. Verify files exist
    index_path = os.path.join('src', 'ui', 'index.html')
    if not os.path.exists(index_path):
        print(f"[ERROR] Could not find '{index_path}'. Ensure you are in the project root directory.")
        sys.exit(1)
        
    # 2. Spin up server thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Allow server a split second to bind
    import time
    time.sleep(0.5)
    
    # 3. Launch browser pointing to the dashboard
    dashboard_url = f"http://localhost:{PORT}/src/ui/index.html"
    print(f"[BROWSER] Opening dashboard at {dashboard_url}...")
    webbrowser.open(dashboard_url)
    
    print("-" * 60)
    print("Dashboard server is active. To stop, press [Ctrl + C].")
    print("-" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping web server... Goodbye!")
        sys.exit(0)
