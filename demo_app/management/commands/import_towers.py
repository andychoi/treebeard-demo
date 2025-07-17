import re
import sys
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from demo_app.models import Tower

TOWER_DATA = {
    "DATA CENTER": {
        "code": "T1000",
        "name": "DATA CENTER",
        "subgroups": [
            {
                "code": "T1100",
                "name": "Data Center Operations",
                "leaves": [
                    {
                        "code": "T1101",
                        "name": "Data Center Facilities & Physical Servers",
                    },
                ],
            },
        ],
    },
    "COMPUTE": {
        "code": "T2000",
        "name": "COMPUTE",
        "subgroups": [
            {
                "code": "T2100",
                "name": "Virtual/Physical Servers",
                "leaves": [
                    {"code": "T2101", "name": "VMware Hosting"},
                    {"code": "T2102", "name": "Windows Hosting"},
                    {"code": "T2103", "name": "Linux Hosting"},
                    {"code": "T2104", "name": "DMZ Hosting"},
                ],
            },
            {
                "code": "T2200",
                "name": "UNIX Systems",
                "leaves": [
                    {"code": "T2201", "name": "AIX Hosting"},
                    {"code": "T2202", "name": "Solaris Hosting"},
                ],
            },
            {
                "code": "T2300",
                "name": "Midrange Systems",
                "leaves": [
                    {"code": "T2301", "name": "AS/400 Hosting"},
                ],
            },
            {
                "code": "T2400",
                "name": "Converged Infrastructure",
                "leaves": [
                    {"code": "T2401", "name": "Converged Infra (e.g., HCI)"},
                ],
            },
            {
                "code": "T2500",
                "name": "Private Cloud",
                "leaves": [
                    {
                        "code": "T2501",
                        "name": "Private Cloud Infrastructure (OpenStack/Nutanix)",
                    },
                    {"code": "T2502", "name": "Public Cloud - AWS/Azure/GCP"},
                    {
                        "code": "T2503",
                        "name": "Cloud Subscription Mgmt (e.g., SaaS)",
                    },
                    {
                        "code": "T2504",
                        "name": "Cloud Cost Optimization / FinOps",
                    },
                ],
            },
        ],
    },
    "STORAGE": {
        "code": "T3000",
        "name": "STORAGE",
        "subgroups": [
            {
                "code": "T3100",
                "name": "Online Storage",
                "leaves": [
                    {"code": "T3101", "name": "SAN/NAS Services"},
                ],
            },
            {
                "code": "T3200",
                "name": "Backup & Archive",
                "leaves": [
                    {"code": "T3201", "name": "Backup/Recovery"},
                ],
            },
        ],
    },
    "NETWORK": {
        "code": "T4000",
        "name": "NETWORK",
        "subgroups": [
            {
                "code": "T4100",
                "name": "LAN/WAN",
                "leaves": [
                    {
                        "code": "T4101",
                        "name": "Network Infra (LAN/WAN/Wi-Fi)",
                    },
                ],
            },
            {
                "code": "T4200",
                "name": "Voice",
                "leaves": [
                    {"code": "T4201", "name": "Voice/VoIP Services"},
                ],
            },
            {
                "code": "T4300",
                "name": "Transport",
                "leaves": [
                    {
                        "code": "T4301",
                        "name": "Connectivity (MPLS, SD-WAN, VPN)",
                    },
                ],
            },
        ],
    },
    "END USER": {
        "code": "T5000",
        "name": "END USER",
        "subgroups": [
            {
                "code": "T5100",
                "name": "Workspace",
                "leaves": [
                    {
                        "code": "T5101",
                        "name": "Client Devices (Laptops/Desktops)",
                    },
                    {"code": "T5102", "name": "VDI (Virtual Desktops)"},
                ],
            },
            {
                "code": "T5200",
                "name": "Mobile Device",
                "leaves": [
                    {
                        "code": "T5201",
                        "name": "Mobile Device Management",
                    },
                ],
            },
            {
                "code": "T5300",
                "name": "Collaboration Tools",
                "leaves": [
                    {"code": "T5301", "name": "Email / O365 / Exchange"},
                    {
                        "code": "T5302",
                        "name": "SharePoint / Teams / OneDrive",
                    },
                ],
            },
            {
                "code": "T5400",
                "name": "Printing",
                "leaves": [
                    {"code": "T5401", "name": "Network Printing"},
                ],
            },
            {
                "code": "T5500",
                "name": "Conferencing",
                "leaves": [
                    {"code": "T5501", "name": "AV / Conferencing Tools"},
                ],
            },
            {
                "code": "T5600",
                "name": "Helpdesk",
                "leaves": [
                    {
                        "code": "T5601",
                        "name": "Helpdesk & Account Services",
                    },
                ],
            },
            {
                "code": "T5700",
                "name": "Deskside Support",
                "leaves": [
                    {"code": "T5701", "name": "Onsite IT Support"},
                ],
            },
        ],
    },
    "APPLICATION": {
        "code": "T6000",
        "name": "APPLICATION",
        "subgroups": [
            {"code": "T6100", "name": "App Development", 
                "leaves": [
                    {"code": "T6101", "name": "SI Project"},
                ],             
            },
            {
                "code": "T6200",
                "name": "App Operations",
                "leaves": [
                    {"code": "T6201", "name": "Business Apps - GMDM"},
                ],
            },
            {
                "code": "T6300",
                "name": "Application Platforms",
                "leaves": [
                    {"code": "T6301", "name": "ERP/CRM Commcercial Platform"},
                ],
            },
            {
                "code": "T6400",
                "name": "Database Services",
                "leaves": [
                    {
                        "code": "T6401",
                        "name": "Oracle / SQL / Tibero DB",
                    },
                    {
                        "code": "T6402",
                        "name": "DB Encryption / Hardening",
                    },
                ],
            },
            {
                "code": "T6500",
                "name": "Middleware",
                "leaves": [
                    {
                        "code": "T6501",
                        "name": "App Servers / ESB / Message Bus",
                    },
                    {
                        "code": "T6502",
                        "name": "Monitoring & Job Scheduling",
                    },
                ],
            },
            {
                "code": "T6600",
                "name": "Data Platform",
                "leaves": [
                    {
                        "code": "T6601",
                        "name": "Big Data Infrastructure (Hadoop, Spark, etc.)",
                    },
                    {
                        "code": "T6602",
                        "name": "ETL / Data Pipeline Management",
                    },
                    {"code": "T6603", "name": "EDW Operations"},
                ],
            },
        ],
    },
    "DELIVERY": {
        "code": "T7000",
        "name": "DELIVERY",
        "subgroups": [
            {
                "code": "T7100",
                "name": "ITSM",
                "leaves": [
                    {
                        "code": "T7101",
                        "name": "Incident / Change / Problem",
                    },
                ],
            },
            {
                "code": "T7200",
                "name": "Project Management",
                "leaves": [
                    {"code": "T7201", "name": "PMO Support"},
                ],
            },
            {
                "code": "T7300",
                "name": "Client Management",
                "leaves": [
                    {
                        "code": "T7301",
                        "name": "Account/Business Relationship Mgmt",
                    },
                ],
            },
            {
                "code": "T7400",
                "name": "Ops Center",
                "leaves": [
                    {
                        "code": "T7401",
                        "name": "NOC / SOC Operations",
                    },
                ],
            },
        ],
    },
    "SECURITY & COMPLIANCE": {
        "code": "T8000",
        "name": "SECURITY & COMPLIANCE",
        "subgroups": [
            {
                "code": "T8100",
                "name": "Security Governance",
                "leaves": [
                    {
                        "code": "T8101",
                        "name": "Sec-Gov/Risk/Compliance/Consulting",
                    },
                    {
                        "code": "T8111",
                        "name": "Network / Infra / App Security",
                    },
                    {
                        "code": "T8112",
                        "name": "Data Loss Prevention / Encryption",
                    },
                ],
            },
            {
                "code": "T8200",
                "name": "Privacy & Compliance",
                "leaves": [
                    {"code": "T8201", "name": "Privacy / eDiscovery"},
                ],
            },
            {
                "code": "T8300",
                "name": "Disaster Recovery",
                "leaves": [
                    {"code": "T8301", "name": "DR Planning & Testing"},
                ],
            },
        ],
    },
    "IT MGMT & ADMIN": {
        "code": "T9000",
        "name": "IT MGMT & ADMIN",
        "subgroups": [
            {
                "code": "T9100",
                "name": "Strategy & Planning",
                "leaves": [
                    {"code": "T9101", "name": "IT Strategy / Planning"},
                ],
            },
            {
                "code": "T9200",
                "name": "Enterprise Architecture",
                "leaves": [
                    {"code": "T9201", "name": "Architecture / Standards"},
                ],
            },
            {
                "code": "T9300",
                "name": "IT Finance",
                "leaves": [
                    {
                        "code": "T9301",
                        "name": "Budget / Costing / Asset Mgmt",
                    },
                ],
            },
        ],
    },
}

def normalize_code(cfg_code, name):
    if cfg_code:
        return cfg_code.upper()[:10]
    slug = re.sub(r"\W+", "", name)
    return slug.upper()[:10]


def get_or_create_node(code, name, parent=None):
    """
    Fetch existing by code or create under `parent`.
    On reparent, uses move(..., pos="sorted-child"|"sorted-sibling") correctly.
    """
    node = Tower.objects.filter(code=code).first()
    if node:
        # update name if changed
        if node.name != name:
            node.name = name
            node.save(update_fields=["name"])
        # reparent if needed
        curr_parent = node.get_parent()
        if parent != curr_parent:
            try:
                if parent is None:
                    node.move(target=None, pos="sorted-sibling")
                else:
                    node.move(target=parent, pos="sorted-child")
            except Exception as e:
                sys.stderr.write(
                    f"[WARN] could not move {code} ({name}) under "
                    f"{parent.code if parent else 'ROOT'}: {e}\n"
                )
    else:
        # create
        try:
            if parent is None:
                node = Tower.add_root(
                    code=code,
                    name=name,
                    description=name,
                    is_active=True,
                )
            else:
                node = parent.add_child(
                    code=code,
                    name=name,
                    description=name,
                    is_active=True,
                )
        except IntegrityError as e:
            # probably code dup; fetch the existing one
            sys.stderr.write(f"[ERROR] inserting {code} — {name}: {e}\n")
            node = Tower.objects.get(code=code)
    return node


class Command(BaseCommand):
    help = "Import or update the entire Tower → L2 → Service hierarchy."

    def handle(self, *args, **opts):
        with transaction.atomic():
            for top_name, cfg in TOWER_DATA.items():
                root_code = normalize_code(cfg.get("code"), cfg["name"])
                root = get_or_create_node(root_code, cfg["name"], parent=None)
                self.stdout.write(self.style.SUCCESS(f"Root: {root.code} — {root.name}"))

                for grp in cfg.get("subgroups", []):
                    lvl2_code = normalize_code(grp.get("code"), grp["name"])
                    lvl2 = get_or_create_node(lvl2_code, grp["name"], parent=root)
                    self.stdout.write(f" └─ {lvl2.code} — {lvl2.name}")

                    for leaf in grp.get("leaves", []):
                        leaf_code = normalize_code(leaf.get("code"), leaf["name"])
                        leaf_node = get_or_create_node(leaf_code, leaf["name"], parent=lvl2)
                        self.stdout.write(f"     └─ {leaf_node.code} — {leaf_node.name}")

            self.stdout.write(self.style.SUCCESS("✅ Tower import/update complete."))