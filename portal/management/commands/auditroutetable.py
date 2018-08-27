import subprocess
from optparse import make_option
from ipaddr import IPNetwork

from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.management.base import BaseCommand, CommandError
from portal.models import Subnet, IPAddress


# Audit these networks. Modify as needed.
NETWORKS = map(IPNetwork, [
    '44.24.240.0/20',
    '44.25.0.0/16',
])
RFC1918 = map(IPNetwork, [
    '10.0.0.0/8',
    '172.16.0.0/12',
    '172.16.0.0/12',
])


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Command(BaseCommand):
    help = 'Compares route table to documented subnets.'
    option_list = BaseCommand.option_list + (
        make_option(
            '--no-color',
            action='store_true',
            dest='no_color',
            default=False,
            help='Disables colorized output.'),
        make_option(
            '-q', '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Hide documented routes.'),
        make_option(
            '-s', '--list-supernets',
            action='store_true',
            dest='supernets',
            default=False,
            help='List supernets of undocumented routes.'),
        )

    def handle(self, *args, **options):
        self.options = options
        self.audit_subnets()

    def audit_subnets(self):
        subnet_map = dict((i.network, i) for i in Subnet.objects.all())
        usernet_map = dict((i.network, i) for i in Subnet.objects.exclude(
            owner=User.objects.get(username='HamWAN')))
        addresses = dict((IPNetwork(i.ip), i) for i in
                         IPAddress.objects.select_related('host').all())

        def format_subnet(routedst):
            owner = subnet_map[routedst].owner
            return str(routedst).ljust(17) + \
                (owner and "[%s] " % str(owner) or "") + \
                subnet_map[routedst].notes

        output = subprocess.check_output(["ip", "r"])
        for line in output.split('\n'):
            try:
                routedst = IPNetwork(line.split(' ')[0])
            except ValueError:
                continue

            if any(routedst in net for net in RFC1918):
                self.write_color(bcolors.FAIL,
                                 str(routedst).ljust(17) + "RFC 1918 leaked into HamWAN")
                continue

            # route is one of our supernets, skip it
            if routedst in NETWORKS:
                continue

            # route is not in HamWAN space, skip it
            if all(routedst not in net for net in NETWORKS):
                continue

            usersupernet = filter(lambda x: routedst in x, usernet_map.keys())
            # matched routes are OK
            if routedst in subnet_map:
                if not self.options['quiet']:
                    self.write_color(bcolors.OKGREEN, format_subnet(routedst))
            # subnets of user-assigned networks are OK
            elif usersupernet:
                if not self.options['quiet']:
                    self.stdout.write('%sdelegated to %s' % (
                                      str(routedst).ljust(17),
                                      str(subnet_map[usersupernet[0]].owner)))
            # /32s that match host records are OK
            elif routedst in addresses:
                if not self.options['quiet']:
                    self.stdout.write(str(routedst).ljust(17) +
                                      addresses[routedst].fqdn())
            else:
                self.write_color(bcolors.FAIL,
                                 str(routedst).ljust(17) + "is in table but not documented")
                if self.options['supernets']:
                    supernets = sorted(
                        filter(lambda x: routedst in x, subnet_map.keys()),
                        key=lambda x: x.prefixlen,
                        reverse=True)
                    if supernets:
                        self.stdout.write('  known supernets:')
                        for net in supernets:
                            self.stdout.write("    " + format_subnet(net))
                        self.stdout.write("\n")

    def write_color(self, color, message):
        if self.options['no_color']:
            self.stdout.write(message)
        else:
            self.stdout.write(color + message + bcolors.ENDC)
