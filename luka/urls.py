"""
URL configuration for luka project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core.home.views import HomeView
from luka import settings as setting, settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", HomeView.as_view(), name='home'),
    path('user/', include('core.user.urls')),
    path('start/', include('core.start.urls')),
    path('login/', include('core.login.urls')),
    # path('company/', include('core.company.urls')),
    # path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if setting.DEBUG:
    urlpatterns += static(setting.MEDIA_URL, document_root=setting.MEDIA_ROOT)
