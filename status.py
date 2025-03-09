import requests
import time
import pytz
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = 'https://discord.com/api/webhooks/1348321504236142613/_5pxDSZ-1B289Vm1wgOBXzxyZWkBrvzTpLue_UZ34xEXWMReVon7bPKA7iWNiM4MdgKm'
MESSAGE_ID = '1348324534901674045'
API_URL = 'http://fi4.bot-hosting.net:22869/'

uptime = timedelta()
downtime = timedelta()
last_check = datetime.now()

def format_time(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def edit_message(embed):
    response = requests.patch(f"{WEBHOOK_URL}/messages/{MESSAGE_ID}", json={
        "content": "API STATUS",  # This is your normal message
        "embeds": [embed]
    })
    return response


def build_embed(status):
    now = datetime.now(pytz.timezone('Europe/Bucharest')).strftime('%Y-%m-%d %I:%M:%S %p')
    color = 0x00FF00 if status == 'Online' else 0xFF0000
    return {
        "title": "API STATUS",
        "color": color,
        "fields": [
            {"name": "Uptime", "value": format_time(uptime), "inline": True},
            {"name": "Downtime", "value": format_time(downtime), "inline": True},
            {"name": "Status", "value": status, "inline": True},
            {"name": "Last Updated (Europe/Bucharest)", "value": now, "inline": False}
        ]
    }

@app.route("/")
def home():
    global uptime, downtime, last_check
    previous_status = None

    while True:
        now = datetime.now()
        elapsed = now - last_check
        last_check = now

        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                uptime += elapsed
                if previous_status != 'Online':
                    embed = build_embed('Online')
                    edit_message(embed)
                previous_status = 'Online'
            else:
                downtime += elapsed
                if previous_status != 'Offline':
                    embed = build_embed('Offline')
                    edit_message(embed)
                previous_status = 'Offline'
        except:
            downtime += elapsed
            if previous_status != 'Offline':
                embed = build_embed('Offline')
                edit_message(embed)
            previous_status = 'Offline'
        
        time.sleep(1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    from http.server import SimpleHTTPRequestHandler, HTTPServer

from http.server import SimpleHTTPRequestHandler, HTTPServer

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>API IS ONLINE</h1></body></html>')
        else:
            super().do_GET()

# Change 8080 to the desired port if needed
server = HTTPServer(('0.0.0.0', 8080), MyHandler)
print("Server running at http://localhost:8080/")

# Run the server
server.serve_forever()
