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

hkey = {'ro.fota.platform':'Platform','ro.build.date.utc':'BuildDate','ro.fota.oem':'Oem','ro.fota.type':'DeviceType', 'ro.fota.device':'Device'}
def clean(data):
   for k,v in data.items():
	if k in hkey.keys():
      	    k = hkey[k]
	data[k] = v.strip()
   return data

def getFilters(data):
    d = {}
    for k,v in data.items():
    	d[k]=v
    return d

def cln(data):    
    logger.info("in cln")
    #logger.info(data)
    if data and len(data)>0:
       	dk=[]
	for da in data:
	    d={}
    	    for k,v in da.items():
	    	#if 'dict' in str(type(v)) and "$id" in v.keys(): logger.info(v.keys())
	    	if k=="partnerName" and ("dict" in str(type(v)) and "$id" in v.keys()):
    	            d['partnerName'] = PartnerRegister.objects(id=v['$id']['$oid']).first().partnerName
            	elif k=="DeviceModel" and ("dict" in str(type(v)) and "$id" in v.keys()):
	            d['DeviceModel'] = ModelRegister.objects(id=v['$id']['$oid']).first().DeviceModel
		elif k=="ActivationDate" and ("dict" in str(type(v)) and "$date" in v.keys()):
		    d["ActivationDate"] = v["$date"]
		    '''elif k=="OngoingUpdates":
		    if not v: d[k]=v
		    else:
			for on in d["OngoingUpdates"]:
			    for x,y in on.items():pass'''
		    
	    	elif k=="Token": pass
	    	elif k=="_id": d["id"] = v["$oid"]
	   	else:
		    d[k]=v
	    dk.append(d)
	return dk
    return data

def case_insensitive(data):
    logger.info(data)
    d={}
    for k,v in data.items():
	d[k] = v.lower()
    return d
