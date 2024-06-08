import paramiko
import time

# Define the SSH details
hostname = '211.255.212.198'
port = 22
username = 'faraaz'
password = 'dracarys'  # It's better to use SSH keys for security

def ssh_connect(hostname, port, username, password):
    try:
        # Create an SSH client object
        client = paramiko.SSHClient()
        # Automatically add the host key if it's not already known
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the Raspberry Pi
        client.connect(hostname, port, username, password)
        print("Connected successfully")
        return client
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def execute_interactive_commands(client, commands):
    try:
        # Open an interactive shell session
        shell = client.invoke_shell()
        for command in commands:
            shell.send(command + '\n')
            time.sleep(2)  # Adjust delay as needed for commands to process
            output = shell.recv(1024).decode('utf-8')
            print(output)
    except Exception as e:
        print(f"Failed to execute command: {e}")

def scan_devices(client):
    try:
        shell = client.invoke_shell()
        shell.send('bluetoothctl\n')
        time.sleep(1)
        shell.send('scan on\n')
        time.sleep(1)

        # Read output for 60 seconds
        end_time = time.time() + 60
        while time.time() < end_time:
            if shell.recv_ready():
                output = shell.recv(1024).decode('utf-8')
                print(output)
            time.sleep(1)  # Adjust as necessary

        # Stop scanning
        shell.send('scan off\n')
        time.sleep(1)
        output = shell.recv(1024).decode('utf-8')
        print(output)

        # Exit bluetoothctl
        shell.send('quit\n')
        time.sleep(1)
    except Exception as e:
        print(f"Failed to execute scan: {e}")

def pair_and_connect_device(client, mac_address):
    commands = [
        f'bluetoothctl pair {mac_address}',
        f'bluetoothctl trust {mac_address}',
        f'bluetoothctl connect {mac_address}',
        'bluetoothctl quit'
    ]
    execute_interactive_commands(client, commands)

if __name__ == "__main__":
    client = ssh_connect(hostname, port, username, password)
    if client:
        scan_devices(client)
        
        # Prompt user for MAC address
        mac_address = input("Enter the MAC address of the device you want to pair and connect: ")
        
        pair_and_connect_device(client, mac_address)
        client.close()
