#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#

from django.db import models
from django.conf import settings
from django.apps import apps
from django.contrib.auth.hashers import make_password, check_password

DEFAULT_PASSWORD_COUNT = 5   # set to 5 to maintain backward compatibility


# Note: A future version of this will likely change to use an ArrayField or JSONField

class UserPasswordHistory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password_1 = models.CharField(blank=True, null=True, max_length=128)
    password_2 = models.CharField(blank=True, null=True, max_length=128)
    password_3 = models.CharField(blank=True, null=True, max_length=128)
    password_4 = models.CharField(blank=True, null=True, max_length=128)
    password_5 = models.CharField(blank=True, null=True, max_length=128)
    password_6 = models.CharField(blank=True, null=True, max_length=128)
    password_7 = models.CharField(blank=True, null=True, max_length=128)
    password_8 = models.CharField(blank=True, null=True, max_length=128)
    password_9 = models.CharField(blank=True, null=True, max_length=128)
    password_10 = models.CharField(blank=True, null=True, max_length=128)
    password_11 = models.CharField(blank=True, null=True, max_length=128)
    password_12 = models.CharField(blank=True, null=True, max_length=128)
    password_13 = models.CharField(blank=True, null=True, max_length=128)
    password_14 = models.CharField(blank=True, null=True, max_length=128)
    password_15 = models.CharField(blank=True, null=True, max_length=128)
    password_16 = models.CharField(blank=True, null=True, max_length=128)
    password_17 = models.CharField(blank=True, null=True, max_length=128)
    password_18 = models.CharField(blank=True, null=True, max_length=128)
    password_19 = models.CharField(blank=True, null=True, max_length=128)
    password_20 = models.CharField(blank=True, null=True, max_length=128)
    password_21 = models.CharField(blank=True, null=True, max_length=128)
    password_22 = models.CharField(blank=True, null=True, max_length=128)
    password_23 = models.CharField(blank=True, null=True, max_length=128)
    password_24 = models.CharField(blank=True, null=True, max_length=128)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + '_password_history'

    def password_is_used(self, password, site_id=1):
        previous_passwords_count = DEFAULT_PASSWORD_COUNT
        SiteSettings = None

        use_site_setting_password_history = getattr(settings, 'USE_SITE_SETTINGS_PASSWORD_HISTORY', False)
        
        try:
            SiteSettings = apps.get_model('setup', 'SiteSettings')
        except:
            SiteSettings = None

        if use_site_setting_password_history and SiteSettings:
            previous_passwords_count = SiteSettings.objects.get(id=site_id).previous_password_count
        else:
            previous_passwords_count = getattr(settings, 'PREVIOUS_PASSWORD_COUNT', DEFAULT_PASSWORD_COUNT)

        if previous_passwords_count:
            for x in range(1, previous_passwords_count + 1):
                f = getattr(self, f'password_{x}', None)
                if f is not None and check_password(password, f):
                    return True

        return False

    def store_password(self):
        for x in range(2, 25)[::-1]:
            """ Shift all the existing passwords """
            setattr(self, f'password_{x}', getattr(self, f'password_{x-1}'))

        self.password_1 = self.user.password
        self.save()
