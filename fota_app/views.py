# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework_mongoengine import viewsets
from rest_framework import permissions
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .errors import *
from .tasks import *
from .helpers import *
import logging
logger = logging.getLogger("fota")

# Create your views here.
class OemConfigView(viewsets.ModelViewSet):
    """
    Oem Config creation view.
    """
    serializer_class = OemConfigSerializer
    queryset = OemConfig.objects
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['post','get','patch']

    def list(self, request):
	logger.info("in device list oem config")
	logger.info(self.request.query_params)
	data = self.request.query_params.copy()
	if data and data['partnerName']:
	    logger.info(data['partnerName'])
	    config = OemConfig.objects(partnerName=data['partnerName'])
	    return Response(json.loads(genRes(config)[0]["config"]), status=status.HTTP_200_OK)
	else: return Response(genRes(self.queryset), status=status.HTTP_200_OK)
        return Response({NDF}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        if request.data:
            data = request.data.copy()    
            srl = OemConfigSerializer(data=data)
            if srl.is_valid(raise_exception=True):
                srl.save()
                return Response({"Success"}, status=status.HTTP_201_CREATED)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)


'''class SomeFilterset(Filterset):
    CurrentBuildVersion = filters.CharFilter()
     = filters.CharFilter('contains')'''

class UpdateGenView(viewsets.ModelViewSet):
    """
    Update generation view.
    """
    serializer_class = UpdateGenSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['post','get','put', 'patch']
    queryset = UpdateGen.objects
    parser_classes = (FormParser, MultiPartParser)

    def list(self, request):
        if self.queryset:
            res = genRes(self.queryset)
            for r in res:
                #rint r
                r['partnerName'] = OemConfig.objects(id=r['partnerName']['$id']['$oid']).first().partnerName
            return Response(res, status=status.HTTP_201_CREATED)
        return Response({NDF}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        data = request.data.copy()
        file_obj = data['File']
        fn = 'files/{}'.format(file_obj.name)
        path = default_storage.save(fn, ContentFile(file_obj.read()))
        tmp_path = os.path.join(settings.MEDIA_ROOT, path)
        data['Md5'] = md5(tmp_path)
        data['DownloadSize'] = humansize(file_obj.size)
        #url = "http://127.0.0.1:8000"+settings.MEDIA_URL+path
        url = settings.MEDIA_URL+path
        data['DownloadUrl'] = url
        data.pop('File')
        x = OemConfig.objects(partnerName=data['partnerName']).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
        srl = UpdateGenSerializer(data=data)
        if srl.is_valid(raise_exception=True):
            srl.save()
            return Response({"Success"}, status=status.HTTP_201_CREATED)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST) 
                        

class DeviceRegisterView(viewsets.ModelViewSet):
    """
    Device registration view.
    """
    serializer_class = DeviceRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = DeviceRegister.objects
    http_method_names = ['post','get','patch']
    parser_classes = (FormParser, MultiPartParser)

    def list(self, request):
        if self.queryset:
            res = genRes(self.queryset)
            return Response(res, status=status.HTTP_201_CREATED)
        return Response({NDF}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        data = request.data.copy()
	logger.info("in device register")
	logger.info(data)
        x = OemConfig.objects(partnerName=data['partnerName']).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
        data['Token'] = uuid.uuid4().hex
	#data['CurrentBuildVersion']='Claymtion_Falcon__1501233644'
        fltr = DeviceRegister.objects(IMEI1=data['IMEI1'], IMEI2=data['IMEI2']).first()
        if fltr: return Response({"Token": getToken(fltr)})
        srl = DeviceRegisterSerializer(data=data)
        if srl.is_valid(raise_exception=True):
            srl.save()
            check_available_updates.delay(data)
            return Response({"Token": data["Token"]}, status=status.HTTP_200_OK)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)


class OemRegisterView(viewsets.ModelViewSet):
    """
    Oem registeration view.
    """
    serializer_class = OemRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = OemRegister.objects
    http_method_names = ['get','post','patch']

    def list(self, request):
        data = self.request.query_params.copy()
        if data and data['partnerName']:
            logger.info(data['partnerName'])
            config = OemRegister.objects(partnerName=data['partnerName'])
            return Response(json.loads(genRes(config)[0]["DeviceModel"]), status=status.HTTP_200_OK)
        else: return Response(genRes(self.queryset), status=status.HTTP_200_OK)
        return Response({NDF}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        data=request.data.copy()
	logger.info(data)
        x = OemConfig.objects(partnerName=data['partnerName']).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
        data['Token'] = uuid.uuid4().hex
        srl = OemRegisterSerializer(data=data)
        if srl.is_valid(raise_exception=True):
            srl.save()
            return Response({"Success"}, status=status.HTTP_200_OK)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)


class CheckUpdateView(viewsets.ModelViewSet):
    """
    Device update check view.
    """
    serializer_class = DeviceRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = DeviceRegister.objects
    http_method_names = ['get','post']

    def list(self, request):
        d = self.request.query_params
	logger.info("in check update")
	logger.info(d)
        #d={'IMEI1': 'imei1', 'IMEI2': 'imei2'}
        device = DeviceRegister.objects(IMEI1=d['IMEI1']).first();logger.info(device)
        if device:
	    logger.info(genRes(device))
	    fltr = {'DeviceModel': device.DeviceModel, 'partnerName': device.partnerName}
            updates = UpdateGen.objects(**fltr);logger.info(updates)
            dtoken = getToken(device)
            if updates:
                oem = OemRegister.objects(**fltr).first();
                if oem:
                    otoken = getToken(oem)
                    m = hashlib.sha1()
                    m.update(otoken)
                    m.update(dtoken)
                    y = []
                    for upd in updates:
                        y.append({'Date': upd.Date, 'UpdateId': upd.id})
                    pop1 = y[0]
                    y.pop(0)
                    device.AvailableUpdates = y
                    device.OngoingUpdates = [pop1]
                    device.save()
                    u = UpdateGen.objects(id=pop1['UpdateId']).first()
                    res = {'updateName': u.UpdateName, 'downloadSize': u.DownloadSize, 
                            'KeyHighLights': u.KeyHighLights, 'downloadURL': u.DownloadUrl, 
                            'md5': u.Md5, 'availVersion': u.AvailVersion, 'auth':m.hexdigest()}
                    return Response(res, status=status.HTTP_200_OK)
        return Response(SF, status=status.HTTP_400_BAD_REQUEST)


class PushUpdatesView(viewsets.ModelViewSet):
    """
    Push update and maintain update logs view.
    """
    serializer_class = UpdateLogsSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = UpdateLogs.objects
    http_method_names = ['get','post']

    def create(self, request):
        data = request.data.copy()
        x = OemConfig.objects(partnerName=data['partnerName']).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
	
        #data['UpdateName'] = 'Update 1'
        up = UpdateGen.objects(UpdateName=data['UpdateName']).first()
        data['Date'] = up['Date']
        y = [{'Date': data['Date'], 'UpdateId': data['UpdateId']}]
        data.pop('UpdateName')
        data['UpdateId'] = getId(up)
        #data['Type'] = "POP"
        if 'IMEI1' in data.keys():
            device = DeviceRegister.objects(IMEI1=data['IMEI1'])
            device.AvailableUpdates = device.AvailableUpdates+y
            device.save()
        else:
            srl = UpdateLogsSerializer(data=data)
            if srl.is_valid(raise_exception=True):
                fltr = {'DeviceModel': data['DeviceModel'], 'partnerName': data['partnerName'], 
                        'CurrentBuildVersion': data['CurrentBuildVersion']}
                devices = DeviceRegister.objects(**fltr)
                if devices:
                    for device in devices:  
                        device.AvailableUpdates = device.AvailableUpdates+y
                        device.save()
                srl.save()
            return Response({"Success"}, status=status.HTTP_200_OK)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)        


class UpdateStatusView(viewsets.ModelViewSet):
    """
    Update status check view.
    """
    serializer_class = DeviceRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = DeviceRegister.objects
    http_method_names = ['post']
    parser_classes = (FormParser, MultiPartParser)

    def create(self, request):
	logger.info(" in update status")
	logger.info(request)
	logger.info(request.data)
	if request.data: logger.info(" in update status")
	else: return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)
	logger.info("data: {}".format(request.data))
        data = request.data.copy()
	data = clean(data)
	logger.info(" in update status")
	logger.info(data)
        x = OemConfig.objects(partnerName=data['partnerName']).first()
	logger.info(x)
	if x:
        	fltr = {'partnerName': x.id, 'IMEI1': data['IMEI1'], 
                	'CurrentBuildVersion': data['CurrentBuildVersion'], 
                	'UpdaterVersion': data['UpdaterVersion']}
		logger.info(fltr)
        	row = DeviceRegister.objects(**fltr).first();logger.info(row)
	        if row:
		    logger.info(data['Status']);logger.info(genRes(row))
	            row.OngoingUpdates[0]['Status'] = data['Status']
		    if not row.DeviceStatus:
			d = row.OngoingUpdates[0]
			y = {'Date': d['Date'], 'UpdateId': d['UpdateId'], 'Status': [data['Status']]}
			row.DeviceStatus = [y]
		    else:
			flg=0
			for ds in row.DeviceStatus:
			    if ds['UpdateId']==row.OngoingUpdates[0]['UpdateId']:
				x = ds['Status']
				x.append(data['Status'])
				ds.Status = x
				flg=1
			if flg==0:
			    d = row.OngoingUpdates
                            y = {'Date': d['Date'], 'UpdateId': d['UpdateId'], 'Status': [data['Status']]}
                            row.DeviceStatus = [y]
	            if data['Status']=='install_complete':
                	row.CompletedUpdates = row.CompletedUpdates + [row.OngoingUpdates[0].pop('Status')]
	                row.OngoingUpdates = []
        	    #elif data['Status'] in ['', 'STATUS_FILE_DAMAGED', \
               	    # 	                'STATUS_INSTALL_CANCEL', 'STATUS_INSTALL_FAIL', 'STATUS_PACKAGE_VERIF_FAILED', \
                    #    	        'STATUS_SHA1_VERIF_FAILED']:
		    '''else:
	                y = row.AvailableUpdates
        	        y.insert(0, row.OngoingUpdates[0].pop('Status'))
                	row.AvailableUpdates = y
	                row.OngoingUpdates = []'''
        	    row.save()         
            	return Response({"Status": True}, status=status.HTTP_200_OK)
        return Response({"Status": False}, status=status.HTTP_400_BAD_REQUEST)

def getList(VAR):
  return [y for y in VAR]

class DevicesView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response(getList(DEVICES))
