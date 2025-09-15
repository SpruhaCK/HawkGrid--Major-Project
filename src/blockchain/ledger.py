import hashlib, json
def push_hash_to_local_log(root_hash):
    with open("logs/blockchain_roots.log","a") as f:
        f.write(root_hash+"\n")