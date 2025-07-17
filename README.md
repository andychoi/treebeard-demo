# Tower & Project Demo with django-treebeard

A small Django demo showing how to use **django-treebeard**’s `MP_Node` to model a hierarchical Tower → Sub-Tower → Service tree, with optional breakdown of child Projects or Applications.

---

## Features

- **Tower model**  
  - Multi-parent tree using `treebeard.mp_tree.MP_Node`  
  - Three levels by convention:  
    1. **Tower** (e.g. DATA CENTER)  
    2. **L2/Sub-Tower** (e.g. T1100)  
    3. **Service** (e.g. T1101)  
  - `breakdown_type` flag lets you declare that a given node will auto-populate children as Projects or Applications.  
  - `requires_breakdown` helper property  

- **Project model**  
  - Flat model with required FK to a top-level Tower (`tower_root`)  
  - Inherits from shared `BaseTypeMixin` + `CBUAllocationMixin`  
  - Standard project fields (code, dates, cost/billing types, etc.)  

- **Application model**  
  - Similar to Project but tied to a Tower  
  - Demo of GMDM/service grouping  
  - Also inherits from `BaseTypeMixin` and links to `tower_root`  

---

## Installation

1. **Install dependencies**  
   ```bash
   pip install Django django-treebeard

	2.	Add to INSTALLED_APPS

INSTALLED_APPS = [
    # …
    'treebeard',
    'your_app_name',  # where these models live
]


	3.	Run migrations

python manage.py makemigrations
python manage.py migrate



⸻

Models Overview

Tower

from treebeard.mp_tree import MP_Node

class Tower(MP_Node, BaseTypeMixin):
    code = models.CharField(max_length=10, unique=True)
    BREAKDOWN_NONE = 'none'
    BREAKDOWN_PROJECT = 'project'
    BREAKDOWN_APP = 'app'

    BREAKDOWN_CHOICES = [
        (BREAKDOWN_NONE, 'No breakdown'),
        (BREAKDOWN_PROJECT, 'One child per Project'),
        (BREAKDOWN_APP, 'One child per Application'),
    ]

    breakdown_type = models.CharField(
        max_length=20,
        choices=BREAKDOWN_CHOICES,
        default=BREAKDOWN_NONE,
        help_text="Auto-populate children under this node"
    )

    node_order_by = ['code']

    class Meta:
        verbose_name = "Tower / Service"

    def __str__(self):
        return f"{self.code} – {self.name}"

    @property
    def level_label(self):
        return {0: 'Tower', 1: 'L2/Sub-Tower', 2: 'Service'}.get(self.get_depth(), f"Level {self.get_depth()}")

    @property
    def str_for_project(self):
        return f"Twr:{self.get_root().code}"

    @property
    def service_type(self):
        return ProjectServiceType.TOWER

    @property
    def requires_breakdown(self):
        return self.breakdown_type != self.BREAKDOWN_NONE

Project

class Project(BaseModelMixin, BaseTypeMixin, CBUAllocationMixin):
    code = models.CharField(max_length=64, unique=True)
    tower_root = models.ForeignKey(
        Tower,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='projects',
        help_text='Categorize this Project under a Tower'
    )
    # … other fields …
    def __str__(self):
        return f"{self.code} – {self.name}"

SimpleGMDMInfo (Application)

class SimpleGMDMInfo(BaseTypeMixin):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    tower_root = models.ForeignKey(
        Tower,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='applications',
        help_text='Categorize this Application under a Tower'
    )

    @property
    def str_for_project(self):
        return f"App:{self.name}:{self.code}"

    @property
    def service_type(self):
        return ProjectServiceType.GMDM


⸻

Usage Examples

Building a Tower tree

from your_app.models import Tower

# create a top-level tower
root = Tower.add_root(code='T1000', name='Datacenter')

# add a sub-tower
sub = root.add_child(code='T1100', name='Compute Services')

# add a service under it
svc = sub.add_child(code='T1101', name='VM Provisioning')

# inspect levels
print(root.level_label)  # "Tower"
print(sub.level_label)   # "L2/Sub-Tower"
print(svc.level_label)   # "Service"

Associating Projects/Applications

from your_app.models import Project, SimpleGMDMInfo

proj = Project.objects.create(
    code='PRJ001',
    name='Billing Platform',
    tower_root=root,
)

app = SimpleGMDMInfo.objects.create(
    code='APP42',
    name='Payment API',
    tower_root=sub,
)


⸻

Admin Registration

from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Tower, Project, SimpleGMDMInfo

class TowerAdmin(TreeAdmin):
    form = movenodeform_factory(Tower)

admin.site.register(Tower, TowerAdmin)
admin.site.register(Project)
admin.site.register(SimpleGMDMInfo)


⸻

License

This demo is provided under the MIT License. Feel free to copy and adapt for your own needs!
