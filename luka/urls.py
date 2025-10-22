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
    path('company/', include('core.company.urls')),
    path('reagent/', include('core.reagent.urls')),
    path('solution/', include('core.solution.urls')),
    # path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if setting.DEBUG:
    urlpatterns += static(setting.MEDIA_URL, document_root=setting.MEDIA_ROOT)
