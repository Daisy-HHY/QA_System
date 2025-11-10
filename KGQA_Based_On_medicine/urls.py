"""KGQA_Based_On_medicine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
import sys
from kgqa import views
from django.http import HttpResponse

urlpatterns = [
    # # path('', home),  # 添加这一行
    # url(r'^kgqa-demo$', views.search_post),
    path('', views.search_post, name='home'),  # 访问根路径时跳转到首页
    re_path(r'^kgqa-demo$', views.search_post, name='kgqa_demo'),
    path('clear/', views.clear_history, name='clear_history'),  # 👈 新增这行
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)