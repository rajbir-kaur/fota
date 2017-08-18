from celery import task
from .models import *
from datetime import datetime as dt
import json
# other imports

@task
def update_last_ping(data):
    device = DeviceM.objects.get(id=data['_id']['$oid'])
    device.lastPingTimestamp = dt.now()
    device.save()
    return None

@task
def check_available_updates(data):
    print data
    avupd = UpdateLogs.objects(DeviceModel=data['DeviceModel'], partnerName=data['partnerName'])
    print avupd
    device = DeviceRegister.objects(Token=data['Token']).first()
    x=[]
    for au in avupd:
        x.append({'UpdateId': au['UpdateId'], 'Date': au['Date']})
    device.AvailableUpdates = x
    device.save()
    return None
