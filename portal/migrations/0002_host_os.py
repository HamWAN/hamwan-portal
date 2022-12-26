# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='os',
            field=models.CharField(max_length=32, null=True, choices=[(b'routeros', b'RouterOS'), (b'airos', b'AirOS'), (b'linux', b'Linux'), (b'esxi', b'ESXi'), (b'windows', b'Windows'), (b'ilo', b'iLO'), (b'other', b'Other'), (None, b'None')]),
            preserve_default=True,
        ),
    ]
