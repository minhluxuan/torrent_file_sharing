import socket
import threading

from concurrent.futures import ThreadPoolExecutor
from helper import main as helper
import json
import os
import time
from dotenv import load_dotenv
import math
from queue import Queue
import random

HOST = '127.0.0.1'
PORT = 65431

load_dotenv()
PIECE_SIZE = int(os.getenv('PIECE_SIZE', '512'))

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
                        f.seek(chunk_index * PIECE_SIZE)
                        data = f.read(PIECE_SIZE)
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
        if response['type'] == 'FILE_CHUNK' and response['info_hash'] == info_hash:
            chunk_data = response['chunk_data']
            
            with open(file_path, "r+b") as f:  
                for i, chunk in enumerate(chunk_data):
                    f.seek(chunk_list[i] * PIECE_SIZE)
                    f.write(chunk.encode('latin1'))
                    print(f"Chunk {chunk_list[i]} has been written into file")
        else:
            print("Has been received invalid response from peer")

def download(info_hash):
    response = helper.get_file_by_info_hash('http://localhost:3000', info_hash)
    if response.status_code != 200:
        print(f"Error: {response.json()['message'] if response.json() else 'An error occurs on tracker side'}")
        return

    if not response.json():
        print('No data were sent from server')
        return

    if not response.json()['data'] or len(response.json()['data']) == 0 or len(response.json()['data'][0]['peers']) == 0:
        print('No peer keeps this file')
        return

    file_name = response.json()['data'][0]['name']
    file_size = response.json()['data'][0]['size']
    server_url = response.json()['data'][0]['trackerUrl']
    file_path = f"storage/{file_name}"

    num_of_pieces = math.ceil(file_size / int(PIECE_SIZE))

    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            pass

    peers_keep_file = response.json()['data'][0]['peers']
    peers_file_status = {}
    chunk_count = {}

    piece_status_lock = threading.Lock()
    chunk_count_lock = threading.Lock()
    piece_download_lock = threading.Lock()
    file_status_lock = threading.Lock()

    connection_queue = Queue()

    for peer in peers_keep_file:
        if peer['address'] != HOST or peer['port'] != PORT:
            connection_queue.put((peer['address'], peer['port']))

    def get_file_status():
        while not connection_queue.empty():
            ip, port = connection_queue.get()
            try:
                peer_ip, peer_port, pieces_status = connect_to_peer_and_get_file_status(ip, port, info_hash)
                if peer_ip and peer_port and pieces_status and len(pieces_status) > 0:
                    if len(pieces_status) != num_of_pieces:
                        continue
                    
                    with piece_status_lock:
                        peers_file_status[(peer_ip, peer_port)] = pieces_status

                    with chunk_count_lock:
                        for chunk_index, has_chunk in enumerate(pieces_status):
                            if has_chunk:
                                if chunk_index not in chunk_count:
                                    chunk_count[chunk_index] = 0
                                chunk_count[chunk_index] += 1
            except:
                print(f"Error connecting to {ip}:{port}")
            connection_queue.task_done()

    with ThreadPoolExecutor(max_workers=5) as executor:
        for _ in range(5):
            executor.submit(get_file_status)

    connection_queue.join()

    chunk_peers_map = {}
    for chunk_index in range(num_of_pieces):
        peers_with_chunk = [(peer, sum(status)) for peer, status in peers_file_status.items() if status[chunk_index]]
        if len(peers_with_chunk) > 0:
            # chunk_peers_map[chunk_index] = sorted(
            #     peers_with_chunk,
            #     key=lambda x: x[1]
            # )
            chunk_peers_map[chunk_index] = peers_with_chunk
            random.shuffle(chunk_peers_map[chunk_index])

    # chunk_peers_map = {
    # '0': [(127.0.0.1, 65432, 2), (127.0.0.1, 65433, 3)]
    # '1': [(127.0.0.1, 65432, 2), (127.0.0.1, 65434, 4)]
    # '2': [(127.0.0.1, 65433, 3), (127.0.0.1, 65435, 5)]
    #}

    chunk_queue = Queue()
    for chunk_index in chunk_peers_map.keys():
        chunk_queue.put(chunk_index)

    piece_has_been_downloaded = [0 for _ in range(num_of_pieces)]

    def download_chunk():
        while not chunk_queue.empty():
            chunk_index = chunk_queue.get()
            peers = chunk_peers_map.get(chunk_index, [])

            for (ip, port), _ in peers:
                with piece_download_lock:
                    if piece_has_been_downloaded[chunk_index] == 1:
                        continue
                
                try:
                    connect_to_peer_and_download_file_chunk(ip, port, info_hash, [chunk_index], file_path)

                    with piece_download_lock:
                        piece_has_been_downloaded[chunk_index] = 1
                    break
                except Exception as e:
                    print(f"Error downloading chunk {chunk_index} from {ip}:{port}: {e}")

            chunk_queue.task_done()

    with ThreadPoolExecutor(max_workers=5) as executor:
        for _ in range(5):
            executor.submit(download_chunk)

    chunk_queue.join()

    def update_file_status():
        with file_status_lock:
            try:
                with open('file_status.json', 'r') as f:
                    file_status_data = json.load(f)
                    if not file_status_data.get(info_hash):
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

    update_file_status()

    response = helper.announce_downloaded(server_url, info_hash, file_name, file_size, HOST, PORT)
    if response.status_code != 201:
        print('Download successfully, announce server failed')
    else:
        print('Download and announce server successfully')


def fetch_file_from_server(server_url):
    response = helper.get_all_files(server_url)
    if response and response.status_code == 200 and response.json() and response.json()['data']:
        print(response.json()['data'])
        
def upload_file_to_server(file_path):
    if not os.path.exists(file_path):
        print(f'Path {file_path} does not exist')
        return

    if not os.path.isfile(file_path):
        print(f'{file_path} is not a file')
        return
    
    info_hash = helper.generate_hash_info(file_path)
    response = helper.upload_file(info_hash, os.path.basename(file_path), HOST, PORT)

    if response == None:
        print('Server is not working now')
        return

    if response.status_code != 201:
        print(f"Upload failed: {response.json()['message']}")
        return

    print('Upload successfully')
    return

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
        elif params[0] == 'upload':
            if not params[1]:
                print('Argument file path is required')
            upload_file_to_server(params[1])
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
        
