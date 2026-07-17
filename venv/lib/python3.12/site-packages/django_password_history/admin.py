#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
# -*- coding: utf-8 -*-

from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin


from .models import (
   UserPasswordHistory,
)


@admin.register(UserPasswordHistory)
class UserPasswordHistoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
   autocomplete_fields = ['user']
   readonly_fields = ('password_1', 'password_2', 'password_3', 'password_4', 'password_5')



