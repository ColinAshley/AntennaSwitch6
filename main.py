# RPi Pico 2 W Antenna Relay Controller
# (C)2025 Bracknell Amateur Radio Club
# Version 1.0a (alpha)
# Toggles six relays ON/OFF ensuring only one relay is ON at any one time

import time
import network
import socket
import machine

# Wi-Fi credentials
ssid = 'SSID'
password = 'PSK Key'

# Define the GPIO pins for the relays
# The pins are active low, so we set them to 1 (HIGH) to keep the relays off initially
relay_pins = [machine.Pin(8, machine.Pin.OUT, value=1),
              machine.Pin(9, machine.Pin.OUT, value=1),
              machine.Pin(10, machine.Pin.OUT, value=1),
              machine.Pin(11, machine.Pin.OUT, value=1),
              machine.Pin(12, machine.Pin.OUT, value=1),
              machine.Pin(13, machine.Pin.OUT, value=1)]

# Connect to Wi-Fi
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        machine.sleep(2)
    print(f'Connected to {ssid}, IP address: {wlan.ifconfig()[0]}')
    return wlan

# HTML for the web page
def web_page():
    # Generate the status of each relay
    relay_status = ""
    for i, pin in enumerate(relay_pins):
        status = "OFF" if pin.value() == 1 else "ON"
        relay_status += f"<li>Antenna {i+1}: {status} <a href=\"?relay={i}\"><button>Select</button></a></li>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BARC Relay Control</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: sans-serif; text-align: center; background-color: #f0f0f0; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border-radius: 8px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin: 10px 0; font-size: 1.2em; }}
            button {{ padding: 10px 20px; font-size: 1em; cursor: pointer; border: none; border-radius: 5px; background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>BARC Wireless Antenna Switch</h1>
            <ul>
                {relay_status}
            </ul>
        </div>
    </body>
    </html>
    """
    return html

# Main program loop
try:
    wlan = connect()
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print('Listening on:', addr)

    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        #print('Content = %s' % request)
        
        # Check for relay toggle request
        relay_toggle_index = request.find('relay=')
        if relay_toggle_index != -1:
            relay_index_str = request[relay_toggle_index+6:relay_toggle_index+7]
            if relay_index_str.isdigit():
                relay_index = int(relay_index_str)
                if 0 <= relay_index < len(relay_pins):
                    # Toggle the relay pin (relays are active low)
                    relay_pins[relay_index].value(not relay_pins[relay_index].value())
                    print(f"Toggled relay {relay_index+1}")

        # Serve the web page
        response = web_page()
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()

except OSError as e:
    print('Connection error:', e)
    machine.reset()