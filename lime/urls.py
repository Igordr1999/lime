"""lime URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include

from home import views as home_views
from data import views as data_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_views.home, name="home"),
    path('reg/', data_views.reg_profile, name="reg"),
    path('login/', data_views.login_profile, name="login"),
    path('logout/', data_views.logout_profile, name="logout"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

