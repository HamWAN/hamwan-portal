from Queue import Queue
from threading import Thread
from optparse import make_option

from easysnmp import snmp_get, snmp_walk, EasySNMPConnectionError, EasySNMPTimeoutError

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.text import slugify
from portal.models import Host, IPAddress

OID_NEIGHBOR_IP = "iso.3.6.1.4.1.14988.1.1.11.1.1.2"
OID_NEIGHBOR_MAC = "iso.3.6.1.4.1.14988.1.1.11.1.1.3"
OID_NEIGHBOR_ID = "iso.3.6.1.4.1.14988.1.1.11.1.1.6"
OID_REG_TABLE = "iso.3.6.1.4.1.14988.1.1.1.2.1.3"
OID_LOCATION = "iso.3.6.1.2.1.1.6.0"
SNMP_ARGS = {
    "community": "hamwan",
    "version": 2,
    "timeout": 2,
    "retries": 1,
}


known_macs = dict((host.wlan_mac.upper(), host) for host in
                  Host.objects.exclude(wlan_mac__exact='').exclude(wlan_mac__isnull=True))
neighbors = {}


def extract_mac_from_oid(oid, prefix=OID_REG_TABLE+"."):
    without_prefix = oid.split(prefix, 1)[1]
    parts = without_prefix.split(".")[:6]
    return ":".join("%02X" % int(i) for i in parts)


def get_neighbors(hostname):
    macs = [i.value for i in snmp_walk(OID_NEIGHBOR_MAC, hostname=hostname, **SNMP_ARGS)]
    macs = [":".join("%02X" % i for i in map(ord, mac)) for mac in macs]
    ips = [i.value for i in snmp_walk(OID_NEIGHBOR_IP, hostname=hostname, **SNMP_ARGS)]
    ids = [i.value for i in snmp_walk(OID_NEIGHBOR_ID, hostname=hostname, **SNMP_ARGS)]
    values = zip(ips, ids)
    return dict(zip(macs, values))


def get_location(hostname):
    """Requests and parses the snmp location from a hostname or address.
    The expected format is: /snmp set location=47.1234,-121.1234"""
    try:
        loc = snmp_get(OID_LOCATION, hostname=hostname, **SNMP_ARGS)
        lat, lon = loc.value.split(',')[0:2]
        return float(lat), float(lon)
    except (ValueError, EasySNMPConnectionError, EasySNMPTimeoutError):
        return None, None


def walk_sector(self, sector, **options):
    try:
        for i in snmp_walk(OID_REG_TABLE, hostname=sector.fqdn(), **SNMP_ARGS):
            mac = extract_mac_from_oid(i.oid)
            if mac in known_macs:
                host = known_macs[mac]
                if options['show_matched']:
                    self.stdout.write("%s on %s matched" % (host.fqdn(), sector))
                old_location = map(str, (host.latitude, host.longitude))
                new_location = get_location(host.fqdn())
                if all(new_location) and map(str, new_location) != old_location:
                    self.stdout.write("%s location changed from %s to %s" % (
                        host.fqdn(),
                        ','.join(old_location),
                        ','.join(map(str, new_location)),
                    ))
                    if not options['dry_run']:
                        host.latitude, host.longitude = new_location
                        host.save()
            else:
                try:
                    neighbors[sector.name]
                except KeyError:
                    neighbors[sector.name] = get_neighbors(sector.fqdn())
                neighbor = neighbors[sector.name].get(mac)
                self.stdout.write("%s on %s not found in portal (neighbor discovery: %s)\n" % (mac, sector,
                    str(neighbor or "disabled")))
                if neighbor:
                    new_host = Host()
                    new_host.name = slugify(unicode(neighbor[1]))
                    new_host.type = "client"
                    new_host.wlan_mac = mac
                    new_host.latitude, new_host.longitude = get_location(neighbor[0])
                    if not options['dry_run']:
                        try:
                            new_host.save()
                        except IntegrityError as e:
                            self.stdout.write(str(e))
                            self.stdout.write("MAC changed. Manual review required to prevent DNS hijack.")
                            continue
                    try:
                        ip = IPAddress.objects.get(ip=neighbor[0])
                        self.stdout.write("Address was previously registered to %s." % str(ip))
                    except IPAddress.DoesNotExist:
                        ip = IPAddress()
                        ip.ip = neighbor[0]
                    ip.host = new_host
                    ip.interface = "wlan1"
                    ip.primary = True
                    if not options['dry_run']:
                        ip.save()
                        print "Added %s" % str(ip)
                else:
                    if not options['dry_run']:
                        self.stdout.write("Cannot automatically add host record without neighbor discovery. "
                                          "Manual intervention required.")
    except (EasySNMPConnectionError, EasySNMPTimeoutError) as e:
        self.stderr.write("%s %s" % (e, sector.fqdn()))


class Command(BaseCommand):
    help = 'Finds unregistered clients connected to sectors and adds them to portal.'
    option_list = BaseCommand.option_list + (
        make_option(
            '--matched',
            action='store_true',
            dest='show_matched',
            default=False,
            help='Show matched MACs as well as unmatched.',
        ),
        make_option(
            '-n', '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Discovers clients but does not add them to portal.',
        ),
    )

    # Future method (Django 1.8+):
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--matched',
    #         action='store_true',
    #         dest='show_matched',
    #         default=False,
    #         help='Show matched MACs as well as unmatched.',
    #     )
    #     parser.add_argument(
    #         '-n', '--dry-run',
    #         action='store_true',
    #         dest='dry_run',
    #         default=False,
    #         help='Discovers clients but does not add them to portal.')

    def handle(self, *args, **options):
        def worker():
            while True:
                args = q.get()
                try:
                    walk_sector(*args, **options)
                finally:
                    q.task_done()
        q = Queue()
        for i in range(10):
            t = Thread(target=worker)
            t.daemon = True
            t.start()
        for sector in Host.objects.filter(type="sector"):
            q.put((self, sector))
        q.join()
