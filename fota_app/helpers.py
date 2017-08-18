import hashlib
import json

def genRes(query):
    print 'gen res', query
    return json.loads(query.to_json())


def getToken(query):
    q = genRes(query)
    print 'get token', q
    return q['Token']['$uuid']


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def getId(query):
    #query = genRes(query)
    return query['_id']['$oid']

def clean(data):
   for k,v in data.items():
	data[k] = v.strip()
   return data
