import subprocess

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from dns.models import Record, Domain

from fields import MACAddressField
from network import IPAddressField, IPNetworkField, IPNetworkQuerySet


domain_validator = RegexValidator(
    regex=r'^(?=^.{2,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)*[a-zA-Z0-9-]{2,63}$)$',
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

    eth_ipv4 = IPAddressField(null=True, blank=True,
        verbose_name="Ethernet IPv4")
    wlan_ipv4 = IPAddressField(null=True, blank=True,
        verbose_name="Wireless IPv4")
    eth_mac = MACAddressField(null=True, blank=True,
        verbose_name="Ethernet MAC")
    wlan_mac = MACAddressField(null=True, blank=True,
        verbose_name="Wireless MAC")
    auto_dns = models.NullBooleanField(null=True, blank=True, default=True,
        verbose_name="Auto manage DNS", help_text="Upon saving, automatically "
        "create an A record and a PTR record for this hostname.")

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

    def _add_dns(self):
        """adds new A and PTR records"""
        new_dns = Record(
            domain=Domain.objects.get(name='hamwan.net'),
            name=self.fqdn().lower(),
            type='A',
            content=(self.eth_ipv4 or self.wlan_ipv4),
            auth=True,
        )
        new_dns.save()

    def _remove_dns(self):
        """removes old DNS records"""
        if self.pk is not None:
            orig = Host.objects.get(pk=self.pk)
            try:
                orig_a = Record.objects.filter(
                    name__iexact=orig.fqdn(), type='A')
                for record in orig_a:
                    record.delete()
                # TODO: should we remove old PTR too, or solve with SQL trigger?
            except Record.DoesNotExist:
                pass

    def delete(self):
        if self.auto_dns:
            self._remove_dns()
        super(Host, self).delete()

    def save(self, *args, **kwargs):
        if self.auto_dns:
            # update DNS records
            self._remove_dns()
            self._add_dns()

        super(Host, self).save(*args, **kwargs)

    def ping(self):
        """ICMP ping the host"""
        return 0 == subprocess.call(
            "ping -c 1 %s" % (self.eth_ipv4 or self.wlan_ipv4),
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.STDOUT)


class Subnet(models.Model):
    """IP address subnet allocations"""
    # override default query manager so we can query for address in subnet
    objects = IPNetworkQuerySet.as_manager()

    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name="subnets_owned", help_text="Warning: changing this field "
        "could affect your ability to administer this server record.")
    network = IPNetworkField()
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.network)

    def clean(self):
        # convert slop like 10.0.1.0/22 to 10.0.0.0/22
        self.network.ip = self.network.network

        # no subnet overlaps allowed
        other_subnets = Subnet.objects.exclude(id=self.id)
        for subnet in other_subnets:
            if self.network in subnet.network or subnet.network in self.network:
                raise ValidationError('Network overlaps with %s (%s)' % (
                    subnet, subnet.notes_short()
                ))

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
