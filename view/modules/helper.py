import requests
import hashlib
from token_store import get_token

def fetch_all_file(base_url, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    response = requests.get(f'{base_url}/file/fetch', headers=headers)
    return response

def publish(server_urls, info_hash, file_name, file_size, address, port):
    for server_url in server_urls:
        try:
            headers = {}
            headers['Authorization'] = f'Bearer {get_token(server_url)}'
            requests.post(f'{server_url}/file/publish', data = { 'infoHash': info_hash, 'name': file_name, 'size': file_size, 'peerAddress': address, 'peerPort': port }, headers=headers)
        except:
            pass

def generate_info_hash(file_path, hash_algorithm = 'sha1'):
    if hash_algorithm == 'sha1':
        hash_func = hashlib.sha1()
    elif hash_algorithm == 'sha256':
        hash_func = hashlib.sha256()
    else:
        raise ValueError("Unsupported hash algorithm. Use 'sha1' or 'sha256'.")

    with open(file_path, 'rb') as file:
        while chunk := file.read(4096):
            hash_func.update(chunk)

    return hash_func.hexdigest()

def fetch_file_by_info_hash(base_url, info_hash, token=None):
    try:
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return requests.get(f'{base_url}/file/fetch?info_hash={info_hash}', headers=headers)
    except:
        return None

def get_file_info_and_peers_keep_file_from_trackers(info_hash, tracker_urls):
    peers_keep_files = []
    file_name = None
    file_size = None

    for tracker_url in tracker_urls:
        response = fetch_file_by_info_hash(tracker_url, info_hash, get_token(tracker_url))
        if response and response.status_code == 200:
            data = response.json().get('data')
            file = data[0] if len(data) > 0 else None
            if file:
                if not file_name:
                    if 'name' in file:
                        file_name = file['name']
                if not file_size:
                    if 'size' in file:
                        file_size = file['size']
                if 'peers' in file and len(file['peers']) > 0:
                    peers = [(peer['address'], peer['port']) for peer in file['peers']]
                    peers_keep_files.extend(peers)

    return file_name, file_size, set(peers_keep_files)

def announce_downloaded(base_url, info_hash, file_name, file_size, peer_address, peer_port):
    return requests.post(f'{base_url}/file/peers/announce', {
        'infoHash': info_hash,
        'fileName': file_name,
        'fileSize': file_size,
        'peerAddress': peer_address,
        'peerPort': peer_port
    })