"""
URL configuration for educate460 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
# from turtle import home

from django.urls import path, include

from core.views.home_view import home
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', home, name='home'),
    path('', include('core.urls')),
    path('django-admin/', RedirectView.as_view(url='/admin-dashboard/', permanent=True)),
    path('admin/', RedirectView.as_view(url='/admin-dashboard/', permanent=True)),
]
    