from Queue import Queue
from threading import Thread
from optparse import make_option

from easysnmp import snmp_get, snmp_walk, EasySNMPTimeoutError

from django.core.management.base import BaseCommand
from portal.models import Host, IPAddress

OID_NEIGHBOR_IP = "iso.3.6.1.4.1.14988.1.1.11.1.1.2"
OID_NEIGHBOR_MAC = "iso.3.6.1.4.1.14988.1.1.11.1.1.3"
OID_NEIGHBOR_ID = "iso.3.6.1.4.1.14988.1.1.11.1.1.6"
OID_REG_TABLE = "iso.3.6.1.4.1.14988.1.1.1.2.1.3"
OID_LOCATION = "iso.3.6.1.2.1.1.6.0"
SNMP_ARGS = {
    "community": "hamwan",
    "version": 2,
}


known_macs = Host.objects.values_list('wlan_mac', flat=True)
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


def walk_sector(self, sector, **options):
    try:
        for i in snmp_walk(OID_REG_TABLE, hostname=sector.fqdn(), **SNMP_ARGS):
            mac = extract_mac_from_oid(i.oid)
            if mac in known_macs:
                if False and show_matched:
                    self.stdout.write("%s on %s matched\n" % (mac, sector))
            else:
                try:
                    neighbors[sector.name]
                except KeyError:
                    neighbors[sector.name] = get_neighbors(sector.fqdn())
                neighbor = neighbors[sector.name].get(mac)
                self.stdout.write("%s on %s not found in portal (neighbor discovery: %s)\n" % (mac, sector,
                    str(neighbor or "disabled")))
                if neighbor:
                    try:
                        ip = IPAddress.objects.get(ip=neighbor[0])
                        self.stdout.write("  %s" % ip.host)
                    except IPAddress.DoesNotExist:
                        new_host = Host()
                        new_host.name = neighbor[1].replace('/', '-')
                        new_host.type = "client"
                        new_host.wlan_mac = mac
                        try:
                            loc = snmp_get(OID_LOCATION, hostname=neighbor[0], **SNMP_ARGS)
                            lat, lon = loc.value.split(',')[0:2]
                            new_host.latitude = float(lat)
                            new_host.longitude = float(lon)
                        except ValueError:
                            pass
                        if not options['dry_run']:
                            new_host.save()
                        ip = IPAddress()
                        ip.host = new_host
                        ip.interface = "wlan1"
                        ip.ip = neighbor[0]
                        ip.primary = True
                        if not options['dry_run']:
                            ip.save()
                        # print " ", repr(new_host)
    except EasySNMPTimeoutError as e:
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
                walk_sector(*args, **options)
                q.task_done()
        q = Queue()
        for i in range(10):
            t = Thread(target=worker)
            t.daemon = True
            t.start()
        for sector in Host.objects.filter(type="sector"):
            q.put((self, sector))
        q.join()
