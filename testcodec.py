import random
import struct
import base64

def generate_key():
    b = []
    for i in range(16):
        b.append(random.randint(0, 255)) 
    r = struct.pack('B'*16, *b)
    return base64.encodebytes(r).decode()

def encode_text(s, key):
    k = base64.decodebytes(key.encode())
    sb = s.encode()
    i = 0
    r = b''
    for b in sb:
        r += bytes([b ^ k[i]])
        i += 1
        if i == len(k):
            i = 0
    return base64.encodebytes(r).decode()

def decode_text(s, key):
    sb = base64.decodebytes(s.encode())
    k = base64.decodebytes(key.encode())
    i = 0
    r = b''
    for b in sb:
        r += bytes([b ^ k[i]])
        i += 1
        if i == len(k):
            i = 0
    return r.decode()
  
