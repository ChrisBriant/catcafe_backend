from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from accounts import views as account_views
#For media
from django.conf.urls.static import static
from django.conf import settings
#Custom claims in token
from .customtoken import CustomTokenObtainPairView

from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('authenticate/',CustomTokenObtainPairView.as_view()),
    url(r'confirm/(?P<hash>\w+)/',account_views.confirm,name='confirm')
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
