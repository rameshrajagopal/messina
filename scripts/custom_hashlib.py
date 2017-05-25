import hashlib

def sha1(token):
    return hashlib.sha1(token).hexdigest()
