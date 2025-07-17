# timesheet/admin.py

from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Tower

@admin.register(Tower)
class TowerAdmin(TreeAdmin):
    """
    Admin for the Tower/Service hierarchy using django-treebeard MP_Node.
    """
    # provide move-node form so you can drag‐and‐drop in the tree
    form = movenodeform_factory(Tower)

    # columns to display in the changelist
    list_display = (
        "code",
        "name",
        "level_label",
        "is_active",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "code",
        "name",
    )

    # optional: show the tree in the detail page
    # TreeAdmin already renders a collapsible tree widget
    # you can customize its behaviour via TreeAdmin attributes if desired.