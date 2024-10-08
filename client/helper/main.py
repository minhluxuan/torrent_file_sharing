import requests
import hashlib

def get_all_files(base_url):
    response = requests.get(f'{base_url}/files')
    return response

def upload_file(hash_info, file_name, address, port):
    response = requests.post('http://localhost:3000/files', data = { 'hashInfo': hash_info, 'name': file_name, 'peerAddress': address, 'peerPort': port })
    return response

def generate_hash_info(file_path, hash_algorithm = 'sha1'):
    if hash_algorithm == 'sha1':
        hash_func = hashlib.sha1()
    elif hash_algorithm == 'sha256':
        hash_func = hashlib.sha256()
    else:
        raise ValueError("Unsupported hash algorithm. Use 'sha1' or 'sha256'.")

    # Đọc file theo từng khối (chunk) để tiết kiệm bộ nhớ
    with open(file_path, 'rb') as file:
        # Đọc file theo từng khối 4096 byte
        while chunk := file.read(4096):
            hash_func.update(chunk)

    # Trả về giá trị hash dưới dạng chuỗi hexa
    return hash_func.hexdigest()

def get_file_by_info_hash(base_url, info_hash):
    return requests.get(f'{base_url}/files?hash_info={info_hash}')

def announce_downloaded(base_url, info_hash, file_name, file_size, peer_address, peer_port):
    return requests.post(f'{base_url}/files/peers/announce', {
        'infoHash': info_hash,
        'fileName': file_name,
        'fileSize': file_size,
        'peerAddress': peer_address,
        'peerPort': peer_port
    })