# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.db.models import Count
try:
    # For Django>=1.7
    from django.apps.apps import get_model
except ImportError:
    # For Django<=1.6
    from django.db.models.loading import get_model
from django.utils.translation import ugettext as _

from parler.admin import TranslatableAdmin
from aldryn_translation_tools.admin import AllTranslationsMixin

from .models import Person, Group


class PersonAdmin(AllTranslationsMixin, TranslatableAdmin):
    list_display = [
        '__str__', 'email', 'vcard_enabled', 'num_groups', ]
    list_filter = ['groups', 'vcard_enabled']
    search_fields = ('translations__name', 'email', 'translations__function')

    def __init__(self, *args, **kwargs):
        """
        Determines if the User widget should be a drop-down or a raw ID field.
        """
        # This is a hack to use until get_raw_id_fields() lands in Django:
        # https://code.djangoproject.com/ticket/17881.
        user_threshold = getattr(
            'settings', 'ALDRYN_PEOPLE_USER_THRESHOLD', 50)
        super(PersonAdmin, self).__init__(*args, **kwargs)
        user_model = getattr(
            settings, 'AUTH_USER_MODEL', 'auth.User').split('.')
        model = get_model(user_model[0], user_model[1])
        if model.objects.count() > user_threshold:
            self.raw_id_fields = ('user', )

    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug', ),
                'function', 'description',
            ),
        }),
        (_('Contact (untranslated)'), {
            'fields': (
                'visual', 'phone', 'mobile', 'fax', 'email', 'website',
                'user', 'vcard_enabled'
            ),
        }),
        (None, {
            'fields': (
                'groups',
            ),
        }),
    )

    def get_queryset(self, request):
        qs = super(PersonAdmin, self).get_queryset(request)
        qs = qs.annotate(group_count=Count('groups'))
        return qs

    def num_groups(self, obj):
        return obj.group_count
    num_groups.short_description = _('# Groups')
    num_groups.admin_order_field = 'group_count'


class GroupAdmin(AllTranslationsMixin, TranslatableAdmin):

    list_display = ['__str__', 'city', 'num_people', ]
    search_filter = ['translations__name']
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug', ),
                'description',
            ),
        }),
        (_('Contact (untranslated)'), {
            'fields': (
                'phone', 'fax', 'email', 'website',
                'address', 'postal_code', 'city'
            )
        }),
    )

    def get_queryset(self, request):
        qs = super(GroupAdmin, self).get_queryset(request)
        qs = qs.annotate(people_count=Count('people'))
        return qs

    def num_people(self, obj):
        return obj.people_count
    num_people.short_description = _('# People')
    num_people.admin_order_field = 'people_count'


admin.site.register(Person, PersonAdmin)
admin.site.register(Group, GroupAdmin)
