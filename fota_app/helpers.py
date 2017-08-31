import hashlib
import json
from .models import *
import logging
logger = logging.getLogger("fota")

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

def getFilters(data):
    d = {}
    for k,v in data.items():
    	d[k]=v
    return d

def cln(data):    
    logger.info("\n\n in cln \n\n")
    logger.info(data)
    if data and len(data)>0:
       	dk=[]
	for da in data:
	    logger.info(da)
	    d={}
    	    for k,v in da.items():
            	logger.info(k);logger.info(type(v))
	    	if 'dict' in str(type(v)) and "$id" in v.keys(): logger.info(v.keys())
	    	if k=="partnerName" and ("dict" in str(type(v)) and "$id" in v.keys()):
        	    #logger.info(PartnerRegister.objects(id=v['$id']['$oid']).first().partnerName)
    	            d['partnerName'] = PartnerRegister.objects(id=v['$id']['$oid']).first().partnerName
            	elif k=="DeviceModel" and ("dict" in str(type(v)) and "$id" in v.keys()):
		    #logger.info(ModelRegister.objects(id=v['$id']['$oid']).first().DeviceModel)
	            d['DeviceModel'] = ModelRegister.objects(id=v['$id']['$oid']).first().DeviceModel
	    	#elif k=="Token": pass
	    	elif k=="_id": d["id"] = v["$oid"]
	   	else:
		    d[k]=v
	    dk.append(d)
	logger.info(dk)
	return dk
    return data

def case_insensitive(data):
    logger.info(data)
    d={}
    for k,v in data.items():
	d[k] = v.lower()
    return d
