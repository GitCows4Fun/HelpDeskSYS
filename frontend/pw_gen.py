import hashlib

passwordlist = [
]

for i in range(len(passwordlist)):
    hashobj = hashlib.sha256() 
    hashobj.update(passwordlist[i].encode('utf-8')) 
    pw_hash = hashobj.hexdigest()
    print(passwordlist[i], pw_hash)
