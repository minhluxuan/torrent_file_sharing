import socket
import threading
from helper import main as helper
import json
import os
import time
from dotenv import load_dotenv
import math

HOST = '127.0.0.1'
PORT = 65433

load_dotenv()
PIECE_SIZE = os.getenv('PIECE_SIZE', '512')

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

        if request['type'] == 'GET_FILE_STATUS':
            info_hash = request['info_hash']

            response = {
                'type': 'FILE_STATUS',
                'info_hash': info_hash,
                'pieces_status': []
            }

            with open('file_status.json', 'r') as f:
                data = json.load(f)

            if not data[info_hash]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            file_name = f"storage/{data[info_hash]['name']}"
            
            response = {
                'type': 'FILE_STATUS',
                'info_hash': info_hash,
                'pieces_status': data[info_hash]['piece_status']
            }

            client_socket.sendall(json.dumps(response).encode('utf-8'))

        elif request['type'] == 'GET_FILE_CHUNK':
            info_hash = request['info_hash']
            chunk_list = request['chunk_list']
            chunk_size = 1
            chunk_data = []

            response = {
                'type': 'FILE_CHUNK',
                'info_hash': info_hash,
                'chunk_data': chunk_data
            }

            with open('file_status.json', 'r') as f:
                data = json.load(f)

            if not data[info_hash]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            file_name = f"storage/{data[info_hash]['name']}"
            
            try:
                with open(file_name, "rb") as f:
                    for chunk_index in chunk_list:
                        f.seek(chunk_index * chunk_size)
                        data = f.read(chunk_size)
                        chunk_data.append(data.decode('latin1'))
            except FileNotFoundError:
                print(f"File {file_name} does not exit.")
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            
            response['chunk_data'] = chunk_data

            client_socket.sendall(json.dumps(response).encode('utf-8'))

def connect_to_peer_and_get_file_status(peer_ip, peer_port, info_hash):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_ip, peer_port))
            print(f"Connected to {peer_ip}:{peer_port}")
            
            request = {
                'type': 'GET_FILE_STATUS',
                'info_hash': info_hash
            }

            s.sendall(json.dumps(request).encode('utf-8'))
            
            response_data = s.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            if response['type'] == 'FILE_STATUS' and response['info_hash'] == info_hash:
                pieces_status = response['pieces_status']
                return peer_ip, peer_port, pieces_status
            else:
                return None, None, None
    except (socket.error, ConnectionRefusedError, TimeoutError) as e:
        print(f"Connection error: {e}")
        return None, None, None

def connect_to_peer_and_download_file_chunk(peer_ip, peer_port, info_hash, chunk_list, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((peer_ip, peer_port))
        print(f"Connected to {peer_ip}:{peer_port}")
        
        request = {
            'type': 'GET_FILE_CHUNK',
            'info_hash': info_hash,
            'chunk_list': chunk_list
        }

        s.sendall(json.dumps(request).encode('utf-8'))
        
        response_data = s.recv(4096)
        response = json.loads(response_data.decode('utf-8'))
        chunk_size = 1
        if response['type'] == 'FILE_CHUNK' and response['info_hash'] == info_hash:
            chunk_data = response['chunk_data']
            
            with open(file_path, "r+b") as f:  
                for i, chunk in enumerate(chunk_data):
                    f.seek(chunk_list[i] * chunk_size)
                    f.write(chunk.encode('latin1'))
                    print(f"Chunk {chunk_list[i]} has been written into file")
        else:
            print("Has been received invalid response from peer")

def download(info_hash):
    response = helper.get_file_by_info_hash('http://localhost:3000', info_hash)
    if (response.status_code != 200):
        print(f"Error: {response.json()['message'] if response.json() else 'An error occurs on tracker side'}")
        return

    if not response.json():
        print('No data were sent from server')

    if not response.json()['data'] or len(response.json()['data']) == 0 or len(response.json()['data'][0]['peers']) == 0:
        print('No peer keeps this file')

    file_name = response.json()['data'][0]['name']
    file_size = response.json()['data'][0]['size']
    server_url = response.json()['data'][0]['trackerUrl']
    file_path = f"storage/{file_name}"

    num_of_pieces = math.ceil(file_size/int(PIECE_SIZE))

    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            pass

    peers_keep_file = response.json()['data'][0]['peers']
    peers_file_status = {}
    chunk_count = {}

    for p in peers_keep_file:
        peer_ip, peer_port, pieces_status = connect_to_peer_and_get_file_status(p['address'], p['port'], info_hash)
        if peer_ip and peer_port and pieces_status and len(pieces_status) > 0:
            if len(pieces_status) != num_of_pieces:
                continue

            peers_file_status[(peer_ip, peer_port)] = pieces_status

            for chunk_index, has_chunk in enumerate(pieces_status):
                    if has_chunk:
                        if chunk_index not in chunk_count:
                            chunk_count[chunk_index] = 0
                        chunk_count[chunk_index] += 1
    
    rarest_chunks = sorted(chunk_count.items(), key=lambda x: x[1])

    piece_has_been_downloaded = [0 for _ in range(num_of_pieces)]
    for chunk_index, _ in rarest_chunks:
        for (ip, port), value in peers_file_status.items():
            if piece_has_been_downloaded[chunk_index] == 1:
                continue

            if value[chunk_index] == True:
                connect_to_peer_and_download_file_chunk(ip, port, info_hash, [chunk_index], file_path)
                piece_has_been_downloaded[chunk_index] = 1

    try:
        with open('file_status.json', 'r') as f:
            file_status_data = json.load(f)
            if not file_status_data[info_hash]:
                file_status_data[info_hash] = {
                    'name': file_name,
                    'piece_status': piece_has_been_downloaded
                }
            else:
                file_status_data[info_hash]['piece_status'] = piece_has_been_downloaded
        
        with open('file_status.json', 'w') as json_file:
            json.dump(file_status_data, json_file, indent=4)
    except FileNotFoundError:
        print('File file_status.json does not exist')

    response = helper.announce_downloaded(server_url, info_hash, file_name, file_size, HOST, PORT)
    if response.status_code != 201:
        print('Download successfully, announce server failed')
    else:
        print('Download and announce server successfully')

def fetch_file_from_server(server_url):
    response = helper.get_all_files(server_url)
    if response and response.status_code == 200 and response.json() and response.json()['data']:
        print(response.json()['data'])
        

def process_input(cmd):
    params = cmd.split()

    if len(params) == 0:
        return
    try:
        if params[0] == 'download':
            if not params[1]:
                print('Argument info_hash is required')
            download(params[1])
        elif params[0] == 'fetch':
            if not params[1]:
                print('Argument server url is required')
            fetch_file_from_server(params[1])
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
        
