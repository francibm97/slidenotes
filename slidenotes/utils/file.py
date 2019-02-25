import hashlib
import os

def is_pdf(file):
    header = file.read(1024)
    file.seek(0)
    magic = b"%PDF-"
    magic_len = len(magic)
    return any(magic == header[i:i + magic_len] for i in range(len(header) - magic_len + 1))

def sha256(file):
    hash = hashlib.sha256()
    for chunk in iter(lambda: file.read(4096), b""):
        hash.update(chunk)
    file.seek(0)
    return hash.hexdigest()
