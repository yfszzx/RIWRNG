"""RIWRNG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from main import views, kernel,autotcm
urlpatterns = [
   # path('admin/', admin.site.urls),
    path('login/', views.login),
    path('auth_error', views.auth_error),
    path('riwrng', views.exp_main),
    path('riwrng/get_result', kernel.get_result),
    path('riwrng/main', views.main),
    path('riwrng/get_compare', kernel.set_compare),
    path('riwrng/performance', views.performance),
    path('riwrng/detail', views.detail),
    path('riwrng/about', views.about),
    path('riwrng/project_performance', views.project_performance),
    path('test/login', views.test_login),
    path('test/debug', views.debug),
    path('riwrng/project_performance', views.project_performance),
    path('autotcm/index', autotcm.index),
]
