# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.utils import OperationalError
import portal.fields
import portal.network
from django.conf import settings
import django.core.validators


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    # postgresql only
    try:
        schema_editor.execute("ALTER TABLE portal_ipaddress ALTER COLUMN ip TYPE inet USING(ip::inet);")
    except OperationalError:
        import sys
        sys.stderr.write("Warning: could not set TYPE inet on ip field. Only supported on postgres.\n")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=242, validators=[django.core.validators.RegexValidator(regex=b'^(?=^.{1,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\\.)*[a-zA-Z0-9-]{1,63}$)$', message=b'Enter a valid hostname.')])),
                ('type', models.CharField(max_length=24, choices=[(b'sector', b'Sector'), (b'ptp', b'PtP'), (b'edgerouter', b'Edge Router'), (b'cellrouter', b'Cell Router'), (b'client', b'Client'), (b'server', b'Server'), (b'anycast', b'Anycast service'), (b'pdu', b'PDU'), (b'kvm', b'KVM/iLO/DRAC'), (b'other', b'Other')])),
                ('eth_mac', portal.fields.MACAddressField(max_length=17, null=True, verbose_name=b'Ethernet MAC', blank=True)),
                ('wlan_mac', portal.fields.MACAddressField(max_length=17, null=True, verbose_name=b'Wireless MAC', blank=True)),
                ('latitude', models.FloatField(help_text=b'Decimal (e.g., 00.0000)', null=True, blank=True)),
                ('longitude', models.FloatField(help_text=b'Decimal (e.g., 000.0000)', null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('admins', models.ManyToManyField(help_text=b'Selected admins will be allowed to edit this host record.', related_name='authorized_hosts', to=settings.AUTH_USER_MODEL, blank=True)),
                ('owner', models.ForeignKey(related_name='hosts_owned', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'Warning: changing this field could affect your ability to administer this host record.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interface', models.CharField(blank=True, max_length=242, null=True, help_text=b'Leave blank for no interface subdomain.', validators=[django.core.validators.RegexValidator(regex=b'^(?=^.{1,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\\.)*[a-zA-Z0-9-]{1,63}$)$', message=b'Enter a valid hostname.')])),
                ('ip', portal.network.IPAddressField(unique=True, verbose_name=b'IP Address')),
                ('auto_dns', models.NullBooleanField(default=True, help_text=b'Upon saving, automatically create an A record and a PTR record for this address.', verbose_name=b'Auto manage DNS')),
                ('primary', models.BooleanField(default=False, help_text=b'Create a CNAME from the host to this interface.')),
                ('host', models.ForeignKey(related_name='ipaddresses', to='portal.Host')),
            ],
            options={
                'ordering': ['ip'],
                'verbose_name': 'IP Address',
                'verbose_name_plural': 'IP Addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, blank=True)),
                ('latitude', models.FloatField(help_text=b'Decimal (e.g., 00.0000)', null=True, blank=True)),
                ('longitude', models.FloatField(help_text=b'Decimal (e.g., 000.0000)', null=True, blank=True)),
                ('status', models.CharField(max_length=30, blank=True)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subnet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', portal.network.IPNetworkField(unique=True)),
                ('notes', models.TextField(blank=True)),
                ('owner', models.ForeignKey(related_name='subnets_owned', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'Warning: changing this field could affect your ability to administer this subnet record.', null=True)),
            ],
            options={
                'ordering': ['network'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='host',
            name='site',
            field=models.ForeignKey(blank=True, to='portal.Site', null=True),
            preserve_default=True,
        ),
        migrations.RunPython(forwards),
    ]
