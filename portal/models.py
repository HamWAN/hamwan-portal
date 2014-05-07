import subprocess

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from dns.models import Record, Domain

from fields import MACAddressField
from network import reverse, IPAddressField, IPNetworkField, IPNetworkQuerySet


domain_validator = RegexValidator(
    regex=r'^(?=^.{1,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)*[a-zA-Z0-9-]{1,63}$)$',
    message="Enter a valid hostname."
)

hostname_validator = RegexValidator(
    regex=r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$',
    message="Only lowercase letters and numbers are allowed.",
)


HOST_TYPES = (
    ('sector', 'Sector'),
    ('ptp', 'PtP'),
    ('edgerouter', 'Edge Router'),
    ('cellrouter', 'Cell Router'),
    ('client', 'Client'),
    ('server', 'Server'),
    ('anycast', 'Anycast service'),
    ('pdu', 'PDU'),
    ('kvm', 'KVM/iLO/DRAC'),
    ('other', 'Other'),
)


class Host(models.Model):
    """Tracks any asset on the network."""
    name = models.CharField(max_length=242, unique=True,
        validators=[domain_validator])
    type = models.CharField(max_length=24, choices=HOST_TYPES)

    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name="hosts_owned", help_text="Warning: changing this field "
        "could affect your ability to administer this host record.")
    admins = models.ManyToManyField('auth.User', blank=True,
        related_name="authorized_hosts",
        help_text="Selected admins will be allowed to edit this host record.")

    eth_mac = MACAddressField(null=True, blank=True,
        verbose_name="Ethernet MAC")
    wlan_mac = MACAddressField(null=True, blank=True,
        verbose_name="Wireless MAC")

    latitude = models.FloatField(null=True, blank=True,
        help_text="Decimal (e.g., 00.0000)")
    longitude = models.FloatField(null=True, blank=True,
        help_text="Decimal (e.g., 000.0000)")

    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def fqdn(self):
        return "%s.hamwan.net" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('portal.views.host_detail', [self.name,])

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig_name = Host.objects.get(pk=self.pk).name
        else:
            orig_name = None

        super(Host, self).save(*args, **kwargs)

        if orig_name and orig_name != self.name:
            for ipaddress in self.ipaddresses.all():
                ipaddress.save()


class IPAddress(models.Model):
    host = models.ForeignKey(Host, related_name='ipaddresses')
    interface = models.CharField(max_length=242, null=True, blank=True,
        validators=[domain_validator],
        help_text="Leave blank for no interface subdomain.")
    ip = IPAddressField(unique=True, verbose_name="IP Address")
    auto_dns = models.NullBooleanField(null=True, blank=True, default=True,
        verbose_name="Auto manage DNS", help_text="Upon saving, automatically "
        "create an A record and a PTR record for this address.")

    def __unicode__(self):
        return "%s (%s)" % (self.fqdn(), self.ip)

    def fqdn(self):
        if self.interface:
            return "%s.%s.hamwan.net" % (self.interface, self.host.name)
        else:
            return "%s.hamwan.net" % (self.host.name)

    def _generate_ptr(self, domain=False):
        rev = str(self.ip).split('.')[::-1]
        return "%s.in-addr.arpa" % '.'.join(rev[1:] if domain else rev)

    def _add_dns(self):
        """adds or updates A and PTR records"""
        new_a, created = Record.objects.get_or_create(
            domain=Domain.objects.get(name='hamwan.net'),
            name=self.fqdn().lower(),
            type='A',
            content=self.ip,
            defaults={'auth': True},
        )
        new_a.save()

        try:
            new_ptr, created = Record.objects.get_or_create(
                domain=Domain.objects.get(name=self._generate_ptr(domain=True)),
                name=self._generate_ptr(),
                type='PTR',
                defaults={'content': self.fqdn().lower(), 'auth': True},
            )
            if not created:
                new_ptr.content = self.fqdn().lower()
            new_ptr.save()
        except Domain.DoesNotExist:
            pass

    def _remove_dns(self):
        """removes old A records"""
        if self.pk is not None:
            orig = IPAddress.objects.get(pk=self.pk)
            try:
                orig_a = Record.objects.filter(
                    name__iexact=orig.fqdn(), type='A')
                for record in orig_a:
                    record.delete()
            except Record.DoesNotExist:
                pass
            try:
                orig_ptr = Record.objects.filter(
                    name=orig._generate_ptr(), type='PTR')
                for record in orig_ptr:
                    record.delete()
            except Record.DoesNotExist:
                pass

    def delete(self):
        if self.auto_dns:
            self._remove_dns()
        super(IPAddress, self).delete()

    def save(self, *args, **kwargs):
        if self.auto_dns:
            # update DNS records
            self._add_dns()

        super(IPAddress, self).save(*args, **kwargs)

    def ping(self):
        """ICMP ping the host"""
        return 0 == subprocess.call(
            "ping -c 1 %s" % (self.ip),
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.STDOUT)

    class Meta:
        ordering = ['ip']
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"


class Subnet(models.Model):
    """IP address subnet allocations"""
    # override default query manager so we can query for address in subnet
    objects = IPNetworkQuerySet.as_manager()

    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name="subnets_owned", help_text="Warning: changing this field "
        "could affect your ability to administer this subnet record.")
    network = IPNetworkField(unique=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.network)

    def clean(self):
        # convert slop like 10.0.1.0/22 to 10.0.0.0/22
        try:
            self.network.ip = self.network.network
        except AttributeError, e:
            raise ValidationError('Could not save network.')

    def get_all_reverse(self):
        ret = []
        for ip in self.network.iterhosts():
            ret.append(reverse(ip))
        return ret

    def max(self):
        return max(self.network)

    def min(self):
        return min(self.network)

    def notes_short(self):
        return self.notes and self.notes.split()[0]

    def numhosts(self):
        return self.network.numhosts
    numhosts.short_description = "Num Hosts"

    @models.permalink
    def get_absolute_url(self):
        return ('portal.views.subnet_detail', [self.network,])

    class Meta:
        ordering = ['network']
