from optparse import make_option
from ipaddr import IPv4Network

from django.core.management.base import BaseCommand, CommandError
from portal.models import Host, Subnet, IPAddress


def max_host(supernet):
    hosts = IPAddress.objects.raw("SELECT * FROM portal_ipaddress "
                                  "WHERE inet %s >> ip "
                                  "ORDER BY ip DESC", [str(supernet)])
    return hosts and hosts[0].ip or None


def max_network(supernet):
    subnets = Subnet.objects.raw("SELECT * FROM portal_subnet "
                                  "WHERE inet %s >> network "
                                  "ORDER BY network DESC", [str(supernet)])
    return subnets and max(subnets[0].network) or None


class Command(BaseCommand):
    args = '<callsign>'
    help = 'Assigns the next OPP pair.'
    option_list = BaseCommand.option_list + (
        make_option(
            '-f',
            action='store_true',
            dest='force',
            default=False,
            help='Force assignment of new OPP pair to previously existing host.',
        ),
        make_option(
            '-n', '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Prints available OPP pair but does not reserve it in the portal.',
        ),
    )

    def handle(self, *args, **options):
        opp_block = Subnet.objects.get(
            notes="HamWAN Open Peering Policy client gateway addresses").network
        last_host = max_host(opp_block)
        last_network = max_network(opp_block)
        if (last_host, last_network) == (None, None):
            pass
        elif last_host > last_network:
            self.stderr.write("WARNING: last host (%s) is not in last subnet (%s)!" % (
                last_host, last_network))

        next31 = IPv4Network(str(max(last_network, last_host) + 1) + '/31')
        hosts = map(str, next31.iterhosts())
        self.stdout.write(" ".join(hosts))
        if options['dry_run']:
            return
        new_host = Host()
        new_host.type = "other"
        try:
            new_host.name = "OPP-%s" % args[0]
        except IndexError:
            raise CommandError("callsign argument required")
        existing = Host.objects.filter(name__iexact=new_host.name)
        if existing:
            self.stderr.write("Callsign matched existing host.")
            if options['force']:
                self.stderr.write("Adding addresses to existing host %s." % new_host.name)
                new_host = existing[0]
            else:
                self.stderr.write("Aborting. Use -f to force adding more addresses to an existing host.")
                return
        new_host.save()
        self.stderr.write(str(new_host))
        for (name, address) in zip(("first", "second"), hosts):
            ip = IPAddress()
            ip.host = new_host
            ip.interface = name
            ip.ip = address
            ip.primary = False
            ip.save()
            self.stderr.write("  " + str(ip))
        subnet = Subnet()
        subnet.network = next31
        subnet.notes = new_host.name
        subnet.save()
