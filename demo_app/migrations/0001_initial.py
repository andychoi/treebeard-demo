# Generated by Django 5.2.4 on 2025-07-17 17:08

import demo_app.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SimpleCBUInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active?"),
                ),
                (
                    "code",
                    models.CharField(
                        blank=True, default=None, max_length=20, null=True
                    ),
                ),
                (
                    "group",
                    models.CharField(
                        blank=True, default=None, max_length=20, null=True
                    ),
                ),
                (
                    "contact",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        null=True,
                        verbose_name="Contact Name",
                    ),
                ),
                (
                    "contact_email",
                    models.EmailField(
                        blank=True,
                        db_index=True,
                        default=None,
                        max_length=255,
                        null=True,
                        verbose_name="Contact Eamil",
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="simplecbu_set",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "CBU",
                "verbose_name_plural": "CBUs",
            },
        ),
        migrations.CreateModel(
            name="Tower",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("path", models.CharField(max_length=255, unique=True)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active?"),
                ),
                (
                    "code",
                    models.CharField(
                        help_text="e.g. T1100, T2101, etc.",
                        max_length=10,
                        unique=True,
                        verbose_name="Code",
                    ),
                ),
                (
                    "breakdown_type",
                    models.CharField(
                        choices=[
                            ("none", "No breakdown"),
                            ("project", "One child per Project"),
                            ("app", "One child per Application"),
                        ],
                        default="none",
                        help_text="Defines whether this tower auto-populates projects or applications under it",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "Tower / Service",
                "verbose_name_plural": "Towers / Services",
                "indexes": [
                    models.Index(fields=["code"], name="demo_app_to_code_7cbafa_idx"),
                    models.Index(
                        fields=["is_active"], name="demo_app_to_is_acti_c719a5_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="SimpleGMDMInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.TextField(blank=True, default=None, null=True)),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active?"),
                ),
                ("code", models.CharField(db_index=True, max_length=10, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("hod", models.CharField(blank=True, max_length=50, null=True)),
                ("manager", models.CharField(blank=True, max_length=50, null=True)),
                ("dept", models.CharField(blank=True, max_length=100, null=True)),
                ("team", models.CharField(blank=True, max_length=100, null=True)),
                ("operator", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "cbu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="demo_app.simplecbuinfo",
                    ),
                ),
                (
                    "tower_root",
                    models.ForeignKey(
                        blank=True,
                        help_text="The Tower under which this application is categorized",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="applications",
                        to="demo_app.tower",
                    ),
                ),
            ],
            options={
                "verbose_name": "Application",
                "verbose_name_plural": "Applications",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_on",
                    models.DateTimeField(auto_now=True, verbose_name="Updated on"),
                ),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active?"),
                ),
                ("code", models.CharField(db_index=True, max_length=64, unique=True)),
                (
                    "internal_order_no",
                    models.CharField(
                        blank=True, db_index=True, max_length=64, null=True
                    ),
                ),
                (
                    "sap_project_code",
                    models.CharField(
                        blank=True, db_index=True, max_length=64, null=True
                    ),
                ),
                (
                    "replicon_work_type",
                    models.CharField(
                        blank=True, db_index=True, max_length=128, null=True
                    ),
                ),
                (
                    "replicon_application",
                    models.CharField(
                        blank=True, db_index=True, max_length=128, null=True
                    ),
                ),
                (
                    "replicon_service",
                    models.CharField(
                        blank=True, db_index=True, max_length=128, null=True
                    ),
                ),
                ("allow_no_task", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="created_by_%(class)s_related",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="updated_by_%(class)s_related",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updated by",
                    ),
                ),
                (
                    "tower_root",
                    models.ForeignKey(
                        blank=True,
                        help_text="The Tower under which this project is categorized",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="projects",
                        to="demo_app.tower",
                    ),
                ),
            ],
            options={
                "ordering": ["code"],
            },
            bases=(models.Model, demo_app.models.CBUAllocationMixin),
        ),
        migrations.CreateModel(
            name="CBUAllocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "allocation",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "cbu",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="cbu_cbuallocation_set",
                        to="demo_app.simplecbuinfo",
                        verbose_name="CBU",
                    ),
                ),
            ],
            options={
                "unique_together": {("content_type", "object_id", "cbu")},
            },
        ),
    ]
