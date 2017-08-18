from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework_mongoengine.validators import UniqueValidator
from .models import *
from rest_framework import serializers
import hashlib


class OemConfigSerializer(DocumentSerializer):
    class Meta:
        model = OemConfig
        fields = '__all__'

class UpdateGenSerializer(DocumentSerializer):
    class Meta:
        model = UpdateGen
        fields = '__all__'
    
class DeviceRegisterSerializer(DocumentSerializer):
    class Meta:
        model = DeviceRegister
        fields = '__all__'

class OemRegisterSerializer(DocumentSerializer):
    class Meta:
        model = OemRegister
        fields = '__all__'

class UpdateLogsSerializer(DocumentSerializer):
    class Meta:
        model = UpdateLogs
        fields = '__all__'
