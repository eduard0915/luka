#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


app_name = 'django_password_history'
urlpatterns = [
    url(
        regex="^UserPasswordHistory/~create/$",
        view=views.UserPasswordHistoryCreateView.as_view(),
        name='UserPasswordHistory_create',
    ),
    url(
        regex="^UserPasswordHistory/(?P<pk>\d+)/~delete/$",
        view=views.UserPasswordHistoryDeleteView.as_view(),
        name='UserPasswordHistory_delete',
    ),
    url(
        regex="^UserPasswordHistory/(?P<pk>\d+)/$",
        view=views.UserPasswordHistoryDetailView.as_view(),
        name='UserPasswordHistory_detail',
    ),
    url(
        regex="^UserPasswordHistory/(?P<pk>\d+)/~update/$",
        view=views.UserPasswordHistoryUpdateView.as_view(),
        name='UserPasswordHistory_update',
    ),
    url(
        regex="^UserPasswordHistory/$",
        view=views.UserPasswordHistoryListView.as_view(),
        name='UserPasswordHistory_list',
    ),
	]
