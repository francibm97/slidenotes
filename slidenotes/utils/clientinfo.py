from flask import request

def get_client_ip():
    return request.remote_addr

def get_client_ua():
    return request.headers.get("User-Agent")

def client_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']
