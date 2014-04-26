# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.core.mail import send_mail
from django.db import models

from hamwanadmin.settings import AMPR_DNS_FROM, AMPR_DNS_TO, AMPR_DNS_QUEUE


RECORD_TYPES = [(a, a) for a in ('A', 'CNAME', 'NS', 'PTR', 'SOA', 'SRV')]


# class Cryptokeys(models.Model):
#     id = models.IntegerField(primary_key=True)
#     domain = models.ForeignKey('Domains', null=True, blank=True)
#     flags = models.IntegerField()
#     active = models.BooleanField(null=True, blank=True)
#     content = models.TextField(blank=True)
#     class Meta:
#         db_table = 'cryptokeys'

# class Domainmetadata(models.Model):
#     id = models.IntegerField(primary_key=True)
#     domain = models.ForeignKey('Domains', null=True, blank=True)
#     kind = models.CharField(max_length=16, blank=True)
#     content = models.TextField(blank=True)
#     class Meta:
#         db_table = 'domainmetadata'

class Domain(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    master = models.CharField(max_length=128, blank=True)
    last_check = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(null=True, blank=True)
    account = models.CharField(max_length=40, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'domains'

class Record(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.ForeignKey(Domain, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=10, blank=True)
    content = models.CharField(max_length=65535, blank=True)
    ttl = models.IntegerField(null=True, blank=True, verbose_name="TTL")
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    ordername = models.CharField(max_length=255, blank=True)
    auth = models.NullBooleanField(null=True, blank=True, default=True,
        verbose_name="Authoritative")

    def __unicode__(self):
        return self.name

    def _generate_ampr_dns(self, command):
        if self.name.endswith('hamwan.net') and self.type in ('A', 'CNAME'):
            name = self.name.split('.net')[0]
            return "%s %s %s %s" % (name, command, self.type, self.content)

    def _generate_ampr_dns_add(self):
        return self._generate_ampr_dns('ADD')

    def _generate_ampr_dns_del(self):
        return self._generate_ampr_dns('DEL')

    def _save_ampr_dns_command(self, command=None):
        with open(AMPR_DNS_QUEUE, 'a') as f:
            f.write("%s\n" % self._generate_ampr_dns_add())

    def _send_ampr_dns_command(self, command=None):
        delete = self._generate_ampr_dns_del()
        add = self._generate_ampr_dns_add()
        send_mail('HamWAN DNS update', '\n'.join([delete, add]),
            AMPR_DNS_FROM, [AMPR_DNS_TO], fail_silently=False)

    def save(self, *args, **kwargs):
        if self.name.endswith('hamwan.net') and self.type in ('A', 'CNAME'):
            self._save_ampr_dns_command()
        super(Record, self).save(*args, **kwargs)

    class Meta:
        db_table = 'records'
        ordering = ['name', 'type', 'content']


# class Supermasters(models.Model):
#     ip = models.GenericIPAddressField()
#     nameserver = models.CharField(max_length=255)
#     account = models.CharField(max_length=40, blank=True)
#     class Meta:
#         db_table = 'supermasters'

# class Tsigkeys(models.Model):
#     id = models.IntegerField(primary_key=True)
#     name = models.CharField(max_length=255, blank=True)
#     algorithm = models.CharField(max_length=50, blank=True)
#     secret = models.CharField(max_length=255, blank=True)
#     class Meta:
#         db_table = 'tsigkeys'

