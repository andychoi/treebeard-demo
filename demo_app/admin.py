from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import (
    Tower,
    SimpleCBUInfo,
    CBUAllocation,
    Project,
    SimpleGMDMInfo,
)


@admin.register(Tower)
class TowerAdmin(TreeAdmin):
    """
    Admin for the Tower/Service hierarchy using django-treebeard MP_Node.
    """
    form = movenodeform_factory(Tower)

    list_display = (
        "code",
        "name",
        "level_label",
        "is_active",
        "breakdown_type",
    )
    list_filter = (
        "breakdown_type",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
    )


class CBUAllocationInline(GenericTabularInline):
    model = CBUAllocation
    extra = 0
    autocomplete_fields = ('cbu',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin for Project with CBU allocations inline.
    """
    list_display = (
        'code',
        'name',
        'tower_root',
        'internal_order_no',
        'sap_project_code',
        'allow_no_task',
        'is_active',
    )
    list_filter = (
        'allow_no_task',
        'is_active',
    )
    search_fields = (
        'code',
        'name',
        'internal_order_no',
        'sap_project_code',
    )
    inlines = (CBUAllocationInline,)


@admin.register(SimpleCBUInfo)
class SimpleCBUInfoAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'group',
        'manager',
        'contact',
        'contact_email',
        'is_active',
    )
    list_filter = (
        'group',
        'is_active',
    )
    search_fields = (
        'code',
        'name',
        'group',
        'contact',
        'contact_email',
    )


@admin.register(SimpleGMDMInfo)
class SimpleGMDMInfoAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'cbu',
        'tower_root',
        'hod',
        'manager',
        'is_active',
    )
    list_filter = (
        'cbu',
        'is_active',
    )
    search_fields = (
        'code',
        'name',
        'hod',
        'manager',
    )


@admin.register(CBUAllocation)
class CBUAllocationAdmin(admin.ModelAdmin):
    list_display = (
        'content_object',
        'cbu',
        'allocation',
    )
    list_filter = (
        'cbu',
    )
    search_fields = (
        'cbu__name',
    )
    raw_id_fields = (
        'content_type',
    )
