from django.conf.urls.static import static
from django.urls import path

from core.user.views.training.views import *
from core.user.views.competence.views import *
from luka import settings
from core.user.views.user.views import *

app_name = 'user'

urlpatterns = [
    path('add/', UserCreateView.as_view(), name='user_create'),
    path('list/', UserListView.as_view(), name='user_list'),
    path('update/<str:slug>/', UserUpdateView.as_view(), name='user_update'),
    # path('update-password/<str:slug>/', UserPasswordUpdateView.as_view(), name='user_password_update'),
    path('detail/<str:slug>/', UserDetailView.as_view(), name='user_detail'),
    # path('profile/<str:slug>/', MyProfileDetailView.as_view(), name='user_profile'),
    # path('profile/edit/<str:slug>/', ProfileUpdateView.as_view(), name='user_profile_update'),
    # path('edit/password/', UserChangePasswordView.as_view(), name='change_password'),
    path('training/add/<uuid:pk>/', TrainingCreateView.as_view(), name='create_training'),
    path('training/update/<uuid:pk>/', TrainingUpdateView.as_view(), name='update_training'),
    path('training/delete/<uuid:pk>/', TrainingDeleteView.as_view(), name='delete_training'),
    path('training/download/', TrainingDownloadView.as_view(), name='download_training'),
    path('competence/add/<uuid:pk>/', CompetenceCreateView.as_view(), name='create_competence'),
    path('competence/update/<uuid:pk>/', CompetenceUpdateView.as_view(), name='update_competence'),
    path('competence/delete/<uuid:pk>/', CompetenceDeleteView.as_view(), name='delete_competence'),
    path('competence/download/', CompetenceDownloadView.as_view(), name='download_competence'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
