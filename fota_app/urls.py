from django.conf.urls import url, include
from .views import *
#from rest_framework.routers import SimpleRouter
from rest_framework_mongoengine.routers import SimpleRouter

router = SimpleRouter()
router.register("deviceConfig", OemConfigView, base_name='oem-config')
router.register("updateGen", UpdateGenView, base_name='update-gen')
router.register("register", DeviceRegisterView, base_name='deviceregister')
router.register("oemRegister", OemRegisterView, base_name='oem-register')
router.register("pushUpdates", PushUpdatesView, base_name='push-updates')
router.register("checkUpdate", CheckUpdateView, base_name='check-update')
router.register("updateStatus", UpdateStatusView, base_name='update-status')

urlpatterns=[
    url(r'',include(router.urls)),
    url(r'^device/$', DevicesView.as_view()),
    #url(r'^update/$', UpdateView.as_view()),
    #url(r'^partner/$', PartnerView.as_view({'post':'create'})),
]

