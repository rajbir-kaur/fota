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
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser, FileUploadParser
from .errors import *
from .tasks import *
from .helpers import *
import binascii
#from drf_mongo_filters import filters, Filterset, ModelFilterset
#from drf_mongo_filters.backend import MongoFilterBackend
import logging
logger = logging.getLogger("fota")

#class PartnerFilter(ModelFilterset):
#    partnerName = filters.CharFilter()
#    class Meta:
#       model = PartnerRegister

# Create your views here.
class PartnerRegisterView(viewsets.ModelViewSet):
    """
    Oem Config creation view.
    """
    serializer_class = PartnerRegisterSerializer
    queryset = PartnerRegister.objects
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['post','get','put','patch']
    parser_classes = (FormParser, MultiPartParser)
#    filter_backends = (MongoFilterBackend,)
#    filter_class = PartnerFilter
    #def get_queryset(self, request):
    #    return PartnerRegister.objects

    def list(self, request):
	logger.info("in device list oem config")
	logger.info(self.request.query_params)
	data = self.request.query_params.copy()
	if data:
	    logger.info(data['partnerName'])
	    config = self.queryset(**getFilters(data))
	    if config: return Response({"config": json.loads(genRes(config)[0]["config"])}, status=status.HTTP_200_OK)
	else: return Response(cln(genRes(self.queryset)), status=status.HTTP_200_OK)

    def create(self, request):
        if request.data:
            data = request.data.copy()
            srl = self.serializer_class(data=data)
            if srl.is_valid(raise_exception=True):
                srl.save()
                return Response({"Success"}, status=status.HTTP_201_CREATED)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, id=None):
	logger.info("in partial update")
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
	    serializer.save()
            return Response(serializer.data)

    def update(self, request, id=None):
        logger.info("\nin update\n")
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


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
	data = self.request.query_params.copy()
        if data:
            config = self.queryset(**getFilters(data))
            if config: return Response(cln(config), status=status.HTTP_200_OK)
        else: return Response(cln(genRes(self.queryset)), status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data.copy()
	logger.info(data)
        file_obj = data['File']
        fn = 'files/{}'.format(file_obj.name);logger.info(fn)
        path = default_storage.save(fn, ContentFile(file_obj.read()));logger.info(path)
	#destination = open('./uploaded_media/'+fn, 'wb+')
   	#for chunk in file_obj.chunks():
        #    destination.write(chunk)
	#destination.close()
        tmp_path = os.path.join(settings.MEDIA_ROOT, fn);logger.info(tmp_path)
        data['Md5'] = md5(tmp_path)
        data['DownloadSize'] = humansize(file_obj.size)
        #url = "http://127.0.0.1:8000"+settings.MEDIA_URL+path
        url = settings.MEDIA_URL+path
	#url = settings.MEDIA_URL+fn	
        data['DownloadUrl'] = url
        data.pop('File')
	#data['File']=""
        x = PartnerRegister.objects(partnerName=data['partnerName']).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
        srl = self.serializer_class(data=data)
        if srl.is_valid(raise_exception=True):
            srl.save()
            return Response({"Success"}, status=status.HTTP_201_CREATED)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST) 

    def partial_update(self, request, id=None):
	print 'in partial update'
        logger.info("in partial update")
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def update(self, request, id=None):
	print 'in update'
        logger.info("\nin update\n")
	row = UpdateGen.objects(id=id).first();logger.info(row)
	data = request.data
	file_obj = data['File']
        fn = 'files/{}'.format(file_obj.name);logger.info(fn)
        path = default_storage.save(fn, ContentFile(file_obj.read()));logger.info(path)
        #destination = open('./uploaded_media/'+fn, 'wb+')
        #for chunk in file_obj.chunks():
        #    destination.write(chunk)
        #destination.close()
        tmp_path = os.path.join(settings.MEDIA_ROOT, fn);logger.info(tmp_path)
        row.Md5 = md5(tmp_path)
        row.DownloadSize = humansize(file_obj.size)
        #url = "http://127.0.0.1:8000"+settings.MEDIA_URL+path
        url = settings.MEDIA_URL+path
        #url = settings.MEDIA_URL+fn    
        row.DownloadUrl = url
        data.pop('File')
        '''serializer = self.serializer_class(data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)                        '''
	row.save()
	return Response(cln(genRes(row)))

class DeviceRegisterView(viewsets.ModelViewSet):
    """
    Device registration view.
    """
    serializer_class = DeviceRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = DeviceRegister.objects
    http_method_names = ['post','get','put','patch']
    parser_classes = (FormParser, MultiPartParser)

    def list(self, request):
        data = self.request.query_params.copy()
        if data:
            config = self.queryset(**getFilters(data))
            if config: return Response(cln(config), status=status.HTTP_200_OK)
        else: return Response(cln(genRes(self.queryset)), status=status.HTTP_200_OK)

    def create(self, request):
	logger.info(request.data.copy())
        data = cln([request.data.copy()])[0]
	logger.info("in device register")
	logger.info(data)
        x = PartnerRegister.objects(partnerName=data['partnerName'].lower()).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
        data['Token'] = uuid.uuid4().hex
	#data['CurrentBuildVersion']='Claymtion_Falcon__1501233644'
        fltr = self.queryset(IMEI1=data['IMEI1'], IMEI2=data['IMEI2']).first()
        if fltr: 
	    if not fltr.CurrentBuildVersion==data['CurrentBuildVersion']:
		fltr.CurrentBuildVersion=data['CurrentBuildVersion']
		fltr.save()
	    return Response({"Token": getToken(fltr)})
        srl = self.serializer_class(data=data)
        if srl.is_valid(raise_exception=True):
            srl.save()
            check_available_updates.delay(data)
            return Response({"Token": data["Token"]}, status=status.HTTP_200_OK)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)


class ModelRegisterView(viewsets.ModelViewSet):
    """
    Oem registeration view.
    """
    serializer_class = ModelRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = ModelRegister.objects
    http_method_names = ['get','post','put','patch']
    parser_classes = (FormParser, MultiPartParser)

    def list(self, request):
        data = self.request.query_params.copy()
        if data:
	    logger.info("in data")
            config = self.queryset(**getFilters(data))
            return Response(cln(config), status=status.HTTP_200_OK)
        else: return Response(cln(genRes(self.queryset)), status=status.HTTP_200_OK)

    def create(self, request):
        data=request.data.copy()
	logger.info(data)
        x = PartnerRegister.objects(partnerName=data['partnerName'].lower()).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x.id
        #data['Token'] = binascii.hexlify(os.urandom(20)).decode()
        data['Token'] = uuid.uuid4().hex
	if data["DeviceModel"]=="LionX1+":
	    data['Token'] = 'fb4587e6a599a968a621f418afbb17a2d1e4c527'
        srl = self.serializer_class(data=data)
        if srl.is_valid(raise_exception=True):
            srl.save()
            return Response({"Token": data['Token']}, status=status.HTTP_200_OK)
        return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, id=None):
        logger.info("in partial update")
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.save()
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def update(self, request, id=None):
        logger.info("\nin update\n")
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.save()
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class CheckUpdateView(viewsets.ModelViewSet):
    """
    Device update check view.
    """
    serializer_class = DeviceRegisterSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = DeviceRegister.objects
    http_method_names = ['get']

    def list(self, request):
        d = self.request.query_params
	logger.info("in check update")
	logger.info(d)
        #d={'IMEI1': 'imei1', 'IMEI2': 'imei2'}
        device = DeviceRegister.objects(IMEI1=d['IMEI1']).first();logger.info(device)
        if device:
	    logger.info(genRes(device));logger.info("in chk update")
	    logger.info(device.partnerName)
	    fltr = {'DeviceModel': device.DeviceModel, 'partnerName': device.partnerName, 'BaseVersion': device.CurrentBuildVersion.strip()};logger.info(fltr)
            updates = UpdateGen.objects(**fltr);logger.info(updates)
            dtoken = getToken(device)
            if updates:
		fltr.pop('BaseVersion')	
                oem = ModelRegister.objects(**fltr).first();logger.info(oem)
                if oem:
                    #otoken = getToken(oem)
		    otoken = oem.Token;logger.info(otoken)
                    m = hashlib.sha1(dtoken+otoken)
                    #m.update(otoken)
                    #m.update(dtoken)
                    y = []
                    for upd in updates:
			logger.info(upd.id)
                        y.append({'Date': dt.now(), 'UpdateId': upd.id})
                    pop1 = y[0]
                    y.pop(0)
                    device.AvailableUpdates = y
                    device.OngoingUpdates = [pop1]
                    device.save()
                    u = UpdateGen.objects(id=pop1['UpdateId']).first()
                    res = {'updateName': u.UpdateName, 'downloadSize': u.DownloadSize, 
                            'KeyHighLights': u.KeyHighLights, 'downloadURL': u.DownloadUrl, 
                            'md5': u.Md5, 'availVersion': u.AvailVersion, 'auth':m.hexdigest()}
		    #if device.IMEI1=='911517400210796': res['auth']='40dcbcea0d9ceacafd075c259c95e3ff81e3af89'
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
    parser_classes = (FormParser, MultiPartParser)

    def list(self, request):
        data = self.request.query_params.copy()
        if data:
            config = self.queryset(**getFilters(data))
            if config: return Response(cln(config), status=status.HTTP_200_OK)
        else: return Response(cln(genRes(self.queryset)), status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data.copy()
        x = PartnerRegister.objects(partnerName=data['partnerName'].lower()).first()
        if not x: return Response({PNF}, status=status.HTTP_400_BAD_REQUEST)
        data['partnerName'] = x
	
        #data['UpdateName'] = 'Update 1'
        up = UpdateGen.objects(UpdateName=data['UpdateName']).first()
        #data['Date'] = up['Date']
        y = [{'Date': dt.now(), 'UpdateId': data['UpdateId']}]
        data.pop('UpdateName')
        data['UpdateId'] = getId(up)
        #data['Type'] = "POP"
        if 'IMEI1' in data.keys():
            device = DeviceRegister.objects(IMEI1=data['IMEI1'])
            device.AvailableUpdates = device.AvailableUpdates+y
            device.save()
        else:
            srl = self.serializer_class(data=data)
            if srl.is_valid(raise_exception=True):
                fltr = {'DeviceModel': data['DeviceModel'], 'partnerName': data['partnerName'].lower()}
                #        'CurrentBuildVersion': data['CurrentBuildVersion']}
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
	data = request.data.copy()
	if request.data: logger.info(" in update status")
	else: return Response({"Error!"}, status=status.HTTP_400_BAD_REQUEST)
	logger.info("data: {}".format(request.data))
        #data = case_insensitive(request.data.copy())
	data = clean(data)
	logger.info(" in update status")
	logger.info(data)
        x = PartnerRegister.objects(partnerName=data['partnerName'].lower()).first()
	logger.info(x)
	if x:
        	fltr = {'IMEI1': data['IMEI1']}
		#	, 
                #	'CurrentBuildVersion': data['CurrentBuildVersion'], 
                #	'UpdaterVersion': data['UpdaterVersion']}
		logger.info(fltr)
        	row = DeviceRegister.objects(**fltr).first();logger.info(row)
	        if row:
		    #logger.info()
		    logger.info(data['Status']);logger.info(genRes(row))
		    if row.OngoingUpdates:
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
			        d = row.OngoingUpdates[0]
                                y = {'Date': d['Date'], 'UpdateId': d['UpdateId'], 'Status': [data['Status']]}
                                row.DeviceStatus = [y]
	                if data['Status']=='install_complete':
			    logger.info(row.OngoingUpdates)
			    d = row.OngoingUpdates[0];d.pop('Status')
                	    row.CompletedUpdates = row.CompletedUpdates + [d]
	                    row.OngoingUpdates = []
			    u = UpdateGen.objects(id=d['UpdateId']).first();logger.info(u)
			    row.CurrentBuildVersion = u.AvailVersion
		        logger.info('####end of row###')
		        logger.info(row)
        	        row.save()         
            	    return Response({"Status": True}, status=status.HTTP_200_OK)
        return Response({"Status": False}, status=status.HTTP_400_BAD_REQUEST)

def getList(VAR):
  return [y for y in VAR]

class DevicesView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response(getList(DEVICES))
