from django.contrib import admin

from core.sampling.models import SamplingGroup, SamplingProcess


class SamplingGroupAdmin(admin.ModelAdmin):
    search_fields = ('id', 'sampling_point', 'hour_sampling', 'number_sampling_day', 'enable_sampling_group')
    list_display = ('id', 'sampling_point', 'hour_sampling', 'number_sampling_day', 'enable_sampling_group')


class SamplingProcessAdmin(admin.ModelAdmin):
    search_fields = ('id', 'group_sampling', 'date_sampling_scheduled', 'date_sampling', 'number_sample',
                     'automatic_sampling', 'sampling_confirmed_by', 'sampling_created_by', 'status_sampling',
                     'batch_number')
    list_display = ('id', 'group_sampling', 'date_sampling_scheduled', 'date_sampling', 'number_sample',
                     'automatic_sampling', 'sampling_confirmed_by', 'sampling_created_by', 'status_sampling',
                     'batch_number')

admin.site.register(SamplingGroup, SamplingGroupAdmin)
admin.site.register(SamplingProcess, SamplingProcessAdmin)
