"""untect_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from app.views import enable_check,go_to_jupyter,restart_device,file_data_save,time_update
from rest_framework import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('enable_check',enable_check),
    path('go_to_jupyter',go_to_jupyter),
    path('api-auth/',include(urls)),
    path('restart_device',restart_device),
    path('file_data_save',file_data_save),
    path('time_update',time_update)
]
