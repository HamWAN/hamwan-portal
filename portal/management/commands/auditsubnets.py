import subprocess
from optparse import make_option
from ipaddr import IPNetwork

from django.core.management.base import BaseCommand, CommandError
from portal.models import Subnet, IPAddress


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
    help = 'Compares route list to documented subnets.'
    option_list = BaseCommand.option_list + (
        make_option('--no-color',
            action='store_true',
            dest='no_color',
            default=False,
            help='Disables colorized output.'),
        make_option('-q', '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Hide documented networks.'),
        )

    def handle(self, *args, **options):
        self.options = options
        self.audit_subnets()

    def audit_subnets(self):
        subnets = [subnet.network for subnet in Subnet.objects.all()]
        addresses = [ipaddress.ip for ipaddress in IPAddress.objects.all()]
        # self.stdout.write(str(subnets))
        output = subprocess.check_output(["ip", "r"])
        for line in output.split('\n'):
            try:
                routedst = IPNetwork(line.split(' ')[0])
            except ValueError:
                continue

            if any(routedst in net for net in RFC1918):
                self.write_color(bcolors.FAIL,
                                 str(routedst) + " in RFC 1918")
                continue

            if all(routedst not in net for net in NETWORKS):
                continue

            if routedst in subnets:
                if not self.options['quiet']:
                    self.write_color(bcolors.OKGREEN, str(routedst))
            elif routedst in addresses:
                if not self.options['quiet']:
                    self.stdout.write(str(routedst) + " host matched")
            else:
                self.write_color(bcolors.FAIL,
                                 str(routedst) + " not documented")

    def write_color(self, color, message):
        if self.options['no_color']:
            self.stdout.write(message)
        else:
            self.stdout.write(color + message + bcolors.ENDC)
