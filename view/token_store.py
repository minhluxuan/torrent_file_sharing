# token_store.py
tokens = {}

def set_token(server, token):
    """Lưu token cho một server."""
    tokens[server] = token

def get_token(server):
    """Lấy token cho một server."""
    return tokens.get(server)

def delete_token(server):
    """Xóa token cho một server."""
    if server in tokens:
        del tokens[server]
