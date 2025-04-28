from django.conf.urls.static import static
from django.urls import path

from luka import settings
from core.user.views import *

app_name = 'user'

urlpatterns = [
    path('add/', UserCreateView.as_view(), name='user_create'),
    path('list/', UserListView.as_view(), name='user_list'),
    # path('update/<str:slug>/', UserUpdateView.as_view(), name='user_update'),
    # path('update-password/<str:slug>/', UserPasswordUpdateView.as_view(), name='user_password_update'),
    # path('detail/<str:slug>/', UserDetailView.as_view(), name='user_detail'),
    # path('profile/<str:slug>/', MyProfileDetailView.as_view(), name='user_profile'),
    # path('profile/edit/<str:slug>/', ProfileUpdateView.as_view(), name='user_profile_update'),
    # path('edit/password/', UserChangePasswordView.as_view(), name='change_password'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
