from ipaddr import IPv4Network

from django.core.management.base import BaseCommand
from portal.models import Subnet, IPAddress


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
    help = 'Returns the next OPP pair.'

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
        self.stdout.write(" ".join(map(str, next31.iterhosts())))
