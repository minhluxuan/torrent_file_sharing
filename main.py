import socket
import threading
import mysql.connector
import pandas as pd
from prettytable import PrettyTable

import json
import os
import time
from dotenv import load_dotenv

HOST = '127.0.0.1'
PORT = 65535

load_dotenv()
config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

try:
    connection = mysql.connector.connect(**config)
    print('Connection successfully')
except mysql.connector.Error as err:
    print(f'Connection error: {err}')

def start_peer_server(peer_ip='127.0.0.1', peer_port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((peer_ip, peer_port))
        server_socket.listen(5)
        print(f"Peer is listening at {peer_ip}:{peer_port}")
        print("Please type your command:\n")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected to {client_address}")
            
            handle_request(client_socket)

def handle_request(client_socket):
    with client_socket:
        data = client_socket.recv(1024).decode('utf-8')
        request = json.loads(data)

        if request['type'] == 'PING':
            response = {
                'type': 'PONG',
            }

            client_socket.sendall(json.dumps(response).encode('utf-8'))

        elif request['type'] == 'DISCOVER':
            client_socket.sendall(json.dumps(response).encode('utf-8'))

def ping_client(peer_ip, peer_port):
    try:
        peer_port = int(peer_port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((peer_ip, peer_port))
            print(f"Connected to {peer_ip}:{peer_port}")
            
            request = {
                'type': 'PING',
            }

            s.sendall(json.dumps(request).encode('utf-8'))
            
            response_data = s.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            if response['type'] == 'PONG':
                print('Client is working')
            else:
                print('Client is not working')
    except (socket.error, ConnectionRefusedError, TimeoutError) as e:
        print('Client is not working')

def get_peers_keep_file(info_hash):
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT f.name, f.infoHash, f.createdAt, f.updatedAt, p.* FROM Files f JOIN PeerOnFiles pof ON f.id = pof.fileId JOIN Peers p ON pof.peerId = p.id WHERE infoHash = %s ', (info_hash,))
        result = cursor.fetchall()
        
        if len(result) > 0:
            print(f'* File name: {result[0][0]}')
            print(f'* Info Hash: {result[0][1]}')
            print(f'* Created Date: {result[0][2]}')

        peers_keep_file = [(pkf[5], pkf[6]) for pkf in result]

        table = PrettyTable()
        table.field_names = ["IP Address", "Port"]

        for peer in peers_keep_file:
            table.add_row(peer)

        print('* Peers keep file:')
        print(table)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()

def process_input(cmd):
    params = cmd.split()

    if len(params) == 0:
        return
    try:
        if params[0] == 'ping':
            if not params[1]:
                print('Argument IP is required')
            if not params[2]:
                print('Argument PORT is required')
            ping_client(params[1], params[2])
        elif params[0] == 'discover':
            if not params[1]:
                print('Argument infohash is required')
            get_peers_keep_file(params[1])
        else:
            print('Invalid command')
    except IndexError as e:
        print('Invalid command')

if __name__ == "__main__":
    try:
        server_thread = threading.Thread(target=start_peer_server, args=(HOST, PORT))
        server_thread.start()

        time.sleep(1)
        while True:
            cmd = input('>>')
            if cmd == 'exit':
                break

            process_input(cmd)
                

    except KeyboardInterrupt:
        print('\nMessenger stopped by user')
    finally:
        print("Cleanup done.")
        
