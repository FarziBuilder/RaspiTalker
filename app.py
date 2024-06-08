from flask import Flask, render_template, request, jsonify
import paramiko
import time
import threading

app = Flask(__name__)

# Define the SSH details
hostname = '211.255.212.198'
port = 22
username = 'faraaz'
password = 'dracarys'  # It's better to use SSH keys for security

client = None
scan_output = ""

def ssh_connect():
    global client
    try:
        # Create an SSH client object
        client = paramiko.SSHClient()
        # Automatically add the host key if it's not already known
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the Raspberry Pi
        client.connect(hostname, port, username, password)
        print("Connected successfully")
    except Exception as e:
        print(f"Failed to connect: {e}")

def scan_devices():
    global scan_output
    try:
        shell = client.invoke_shell()
        shell.send('bluetoothctl\n')
        time.sleep(1)
        shell.send('scan on\n')
        time.sleep(1)

        # Read output for 60 seconds
        scan_output = ""
        end_time = time.time() + 60
        while time.time() < end_time:
            if shell.recv_ready():
                output = shell.recv(1024).decode('utf-8')
                scan_output += output
            time.sleep(1)  # Adjust as necessary

        # Stop scanning
        shell.send('scan off\n')
        time.sleep(1)
        output = shell.recv(1024).decode('utf-8')
        scan_output += output

        # Exit bluetoothctl
        shell.send('quit\n')
        time.sleep(1)
    except Exception as e:
        print(f"Failed to execute scan: {e}")

def pair_and_connect_device(mac_address):
    try:
        shell = client.invoke_shell()
        shell.send('bluetoothctl\n')
        time.sleep(1)
        commands = [
            f'pair {mac_address}\n',
            f'trust {mac_address}\n',
            f'connect {mac_address}\n',
            'quit\n'
        ]
        for command in commands:
            shell.send(command)
            time.sleep(2)
            output = shell.recv(1024).decode('utf-8')
            print(output)
    except Exception as e:
        print(f"Failed to execute command: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    threading.Thread(target=scan_devices).start()
    return jsonify({"status": "Scanning started"})

@app.route('/connect_device', methods=['POST'])
def connect_device():
    mac_address = request.form['mac_address']
    pair_and_connect_device(mac_address)
    return jsonify({"status": f"Attempted to connect to {mac_address}"})

@app.route('/get_scan_output', methods=['GET'])
def get_scan_output():
    global scan_output
    return jsonify({"scan_output": scan_output})

if __name__ == '__main__':
    ssh_connect()
    app.run(host='0.0.0.0', port=5000)
