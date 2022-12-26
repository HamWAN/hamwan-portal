# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_host_os'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='type',
            field=models.CharField(max_length=24, choices=[(b'sector', b'Sector'), (b'ptp', b'PtP'), (b'edgerouter', b'Edge Router'), (b'cellrouter', b'Cell Router'), (b'client', b'Client'), (b'server', b'Server'), (b'vm', b'Virtual Machine'), (b'container', b'Container'), (b'anycast', b'Anycast service'), (b'pdu', b'PDU'), (b'kvm', b'KVM/iLO/DRAC'), (b'other', b'Other')]),
            preserve_default=True,
        ),
    ]
