import subprocess
from ipaddr import IPNetwork

from django.core.management.base import BaseCommand, CommandError
from portal.models import Subnet, IPAddress


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

    def handle(self, *args, **options):
        subnets = [subnet.network for subnet in Subnet.objects.all()]
        addresses = [ipaddress.ip for ipaddress in IPAddress.objects.all()]
        # self.stdout.write(str(subnets))
        output = subprocess.check_output(["ip", "r"])
        for line in output.split('\n'):
            try:
                routedst = IPNetwork(line.split(' ')[0])
            except ValueError:
                continue

            if routedst not in IPNetwork('44.24.240.0/20'):
                continue

            if routedst in subnets:
                message = bcolors.OKGREEN + str(routedst)
            elif routedst in addresses:
                message = str(routedst) + " host matched"
            else:
                message = bcolors.FAIL + str(routedst) + " not documented"
            self.stdout.write(message + bcolors.ENDC)
