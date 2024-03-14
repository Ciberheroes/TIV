import secrets

key = secrets.token_bytes(256)

print(key.hex())