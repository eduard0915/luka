#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
# -*- coding: utf-8 -*-

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	UserPasswordHistory,
)


class UserPasswordHistoryCreateView(CreateView):

    model = UserPasswordHistory


class UserPasswordHistoryDeleteView(DeleteView):

    model = UserPasswordHistory


class UserPasswordHistoryDetailView(DetailView):

    model = UserPasswordHistory


class UserPasswordHistoryUpdateView(UpdateView):

    model = UserPasswordHistory


class UserPasswordHistoryListView(ListView):

    model = UserPasswordHistory

