# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime as dt

DEVICES= ('Phone', 'TV', 'Auto', 'Wear')

# Create your models here.
class PartnerRegister(Document):
    partnerName = fields.StringField(unique=True)
    config = fields.StringField()

class DeviceRegister(Document):
    partnerName = fields.ReferenceField(PartnerRegister, dbref=True, required=True)
    Token = fields.UUIDField(unique=True)
    IMEI1 = fields.StringField(unique=True, required=True)
    IMEI2 = fields.StringField(unique=True, required=True)
    DeviceId = fields.StringField()
    DeviceModel = fields.StringField()
    DeviceBrand = fields.StringField()
    UpdaterVersion = fields.StringField()
    ActivationDate = fields.DateTimeField(default=dt.now())
    releaseSoftware = fields.StringField()
    CurrentBuildVersion = fields.StringField()
    AvailableUpdates = fields.ListField()
    CompletedUpdates = fields.ListField()
    OngoingUpdates = fields.ListField()
    DeviceStatus = fields.ListField()

class UpdateGen(Document):
    UpdateName = fields.StringField()
    partnerName = fields.ReferenceField(PartnerRegister, dbref=True, required=True)
    AvailVersion = fields.StringField()
    BaseVersion = fields.StringField()
    ChangeLog = fields.StringField()
    File = fields.FileField()
    DeviceType = fields.StringField(max_length=5, choices=DEVICES)
    DeviceModel = fields.StringField()
    DownloadSize = fields.StringField()
    KeyHighLights = fields.StringField()
    Md5 = fields.StringField()
    DownloadUrl = fields.StringField() 
    Date = fields.DateTimeField(default=dt.now())

class ModelRegister(Document):
    partnerName = fields.ReferenceField(PartnerRegister, dbref=True, required=True)
    DeviceModel = fields.StringField()
    #Token = fields.UUIDField(unique=True) 
    Token = fields.StringField()

class UpdateLogs(Document):
    UpdateId = fields.ReferenceField(UpdateGen, dbref=True, required=True)
    Date = fields.DateTimeField()
    DeviceModel = fields.StringField()
    partnerName = fields.ReferenceField(PartnerRegister, dbref=True, required=True)
