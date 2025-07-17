from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from enum import Enum
class AbstractIntEnums(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.value[0], i.value[1]) for i in cls)
    @classmethod
    def text_map(cls):
        return dict((i.value[0], i.value[1]) for i in cls)
    @classmethod
    def name_map(cls):
        return dict((i.name, i.value[0]) for i in cls)
    @classmethod
    def get_value(cls, name):
        return cls[name].value[0]
    @classmethod
    def get_text(cls, value):
        return cls.text_map().get(value)

class ProjectServiceType(AbstractIntEnums):
    GMDM = 1, "GMDM"
    TOWER = 2, "Tower"
    COST_CENTER = 3, "Cost Center"
    OTHERS = 4, "Others"


class BaseCreateRecordMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        _("Created at"), auto_now_add=True, editable=False
    )
    created_by = models.ForeignKey(
        get_user_model(),
        related_name="created_by_%(class)s_related",
        verbose_name=_("Created by"),
        on_delete=models.DO_NOTHING,
        null=True,
    )


class BaseUpdateRecordMixin(models.Model):
    class Meta:
        abstract = True

    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name="updated_by_%(class)s_related",
        verbose_name=_("Updated by"),
        null=True,
    )
    updated_on = models.DateTimeField(_("Updated on"), auto_now=True, editable=False)


class BaseModelMixin(BaseCreateRecordMixin, BaseUpdateRecordMixin):
    class Meta:
        abstract = True


class BaseTypeMixin(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(default=None, blank=True, null=True)
    is_active = models.BooleanField(verbose_name=_("Is active?"), default=True)

    def __str__(self):
        return f"{self.name}"


class SimpleCBUInfo(BaseTypeMixin):
    class Meta:
        verbose_name = "CBU"
        verbose_name_plural = "CBUs"
    code = models.CharField(max_length=20, blank=True, null=True, default=None)
    group = models.CharField(max_length=20, blank=True, null=True, default=None)
    manager = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name="simplecbu_set",
        blank=True,
        null=True,
    )
    contact = models.CharField(
        max_length=128,
        verbose_name=_("Contact Name"),
        blank=True,
        null=True,
    )
    contact_email = models.EmailField(
        max_length=255,
        verbose_name=_("Contact Eamil"),
        db_index=True,
        default=None,
        null=True,
        blank=True,
    )

class CBUAllocation(models.Model):
    class Meta:
        unique_together = (("content_type", "object_id", "cbu"),)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    cbu = models.ForeignKey(
        SimpleCBUInfo,
        on_delete=models.DO_NOTHING,
        related_name="cbu_cbuallocation_set",
        verbose_name=_("CBU"),
        blank=False,
        null=False,
    )
    allocation = models.DecimalField(decimal_places=2, max_digits=5, default=0)


class CBUAllocationMixin:
    cbu_allocations = GenericRelation(CBUAllocation)

    def reset_cbu_allocation(self):
        keys = get_content_object(self)
        CBUAllocation.objects.filter(**keys).delete()

    def set_cbu_allocation(self, cbu, pct=0):
        keys = get_content_object(self)
        keys.update({"cbu": cbu})
        kwargs = {"allocation": pct}
        CBUAllocation.objects.update_or_create(**keys, defaults=kwargs)

    def get_cbu_allocation_data(self):
        return CBUAllocation.objects.filter(**get_content_object(self)).order_by(
            "cbu__name"
        )

    def get_cbu_allocation_text(self, is_full=False):
        # print(self.get_cbu_allocation_data().values_list('cbu__group', flat=True).distinct())
        cbu_list = list(
            self.get_cbu_allocation_data()
            .values_list("cbu__group", flat=True)
            .distinct()
        )
        cbu_cnt = len(cbu_list)
        if cbu_cnt > 0:
            if cbu_cnt > 1:
                if is_full:
                    return ", ".join(cbu_list)
                else:
                    return f"{cbu_list[0]} and {cbu_cnt-1} more.."
            else:
                return cbu_list[0]
        else:
            return ""



class Tower(MP_Node, BaseTypeMixin):
    """
    A single tree storing:
      • level 0 = top‐level “Tower” (e.g. DATA CENTER)
      • level 1 = L2/Sub-Tower (e.g. T1100)
      • level 2 = Service (e.g. T1101)
    """

    code = models.CharField(
        _("Code"),
        max_length=10,
        unique=True,
        help_text=_("e.g. T1100, T2101, etc."),
    )

    BREAKDOWN_NONE    = 'none'
    BREAKDOWN_PROJECT = 'project'
    BREAKDOWN_APP     = 'app'
    BREAKDOWN_CHOICES = [
        (BREAKDOWN_NONE,    'No breakdown'),
        (BREAKDOWN_PROJECT, 'One child per Project'),
        (BREAKDOWN_APP,     'One child per Application'),
    ]
    breakdown_type = models.CharField(
        max_length=20,
        choices=BREAKDOWN_CHOICES,
        default=BREAKDOWN_NONE,
        help_text="Defines whether this tower auto-populates projects or applications under it",
    )

    # tell treebeard how to order siblings
    node_order_by = ['code']

    class Meta:
        verbose_name = _("Tower / Service")
        verbose_name_plural = _("Towers / Services")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} – {self.name}"

    @property
    def level_label(self) -> str:
        """Human-friendly level name."""
        return {0: "Tower", 1: "L2/Sub-Tower", 2: "Service"}.get(self.get_depth(), f"Level {self.get_depth()}")

    @property
    def str_for_project(self) -> str:
        """
        For your `Project.service` GenericForeignKey – we’ll still
        label it by the top‐level code:
        """
        return f"Twr:{self.get_root().code}"

    @property
    def service_type(self):
        return ProjectServiceType.TOWER
    
    @property
    def requires_breakdown(self):
        return self.breakdown_type != self.BREAKDOWN_NONE


class Project(
    BaseModelMixin,
    BaseTypeMixin,
    CBUAllocationMixin
):
    # Basic fields
    code = models.CharField(max_length=64, db_index=True, unique=True)
    tower_root = models.ForeignKey(
        Tower,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='projects',
        help_text='The Tower under which this project is categorized',
    )

    # existing fields...
    # program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, null=True, blank=True)
    # work_type = models.ForeignKey(ProjectWorkType, on_delete=models.DO_NOTHING, null=True, blank=True)

    # # generic link to any service-type (Tower, GMDM, CostCenter, Others)
    # service_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    # service_object_id = models.PositiveIntegerField(null=True, blank=True)
    # service = GenericForeignKey('service_type', 'service_object_id')

    # phase = models.IntegerField(choices=choices.ProjectPhase.choices(), default=choices.ProjectPhase.IDEATION.value[0])
    # manager = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True)
    # approver = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True, related_name='project_approver')
    # dept = models.ForeignKey(common_models.SimpleDepartmentInfo, on_delete=models.DO_NOTHING, null=True, blank=True)

    # date_start = models.DateField(null=True, blank=True)
    # date_end = models.DateField(null=True, blank=True)

    # cost_type = models.SmallIntegerField(choices=choices.ProjectCostType.choices(), default=choices.ProjectCostType.UNCLASSIFIED.value[0])
    # billing_type = models.SmallIntegerField(choices=choices.ProjectBillingType.choices(), default=choices.ProjectBillingType.TIME_AND_MATERIAL.value[0])

    internal_order_no  = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    sap_project_code   = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    replicon_work_type = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    replicon_application = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    replicon_service = models.CharField(max_length=128, null=True, blank=True, db_index=True)

    allow_no_task = models.BooleanField(default=False)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def phase_text(self):
        return choices.ProjectPhase.get_text(self.phase)

    @property
    def cost_type_text(self):
        return choices.ProjectCostType.get_text(self.cost_type)

    @property
    def billing_type_text(self):
        return choices.ProjectBillingType.get_text(self.billing_type)


class SimpleGMDMInfo(BaseTypeMixin):
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    cbu = models.ForeignKey(SimpleCBUInfo, on_delete=models.DO_NOTHING, null=True, blank=True)
    hod = models.CharField(max_length=50, null=True, blank=True)
    manager = models.CharField(max_length=50, null=True, blank=True)
    dept = models.CharField(max_length=100, null=True, blank=True)
    team = models.CharField(max_length=100, null=True, blank=True)
    operator = models.CharField(max_length=100, null=True, blank=True)

    tower_root = models.ForeignKey(
        Tower,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='applications',
        help_text='The Tower under which this application is categorized',
    )

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        ordering = ['code']

    @property
    def str_for_project(self):
        return f"App:{self.name}:{self.code}"

    @property
    def service_type(self):
        return ProjectServiceType.GMDM
