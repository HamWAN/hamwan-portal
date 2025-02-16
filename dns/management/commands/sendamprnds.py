import os
os.environ['http_proxy']=''
import urllib2

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from config.settings import AMPR_DNS_FROM, AMPR_DNS_TO, AMPR_DNS_QUEUE


class Command(BaseCommand):
    help = 'Sends queued AMPR DNS robot commands'
    ampr_hosts = []

    def handle(self, *args, **options):
        to_ampr = []
        with open(AMPR_DNS_QUEUE, 'r') as f:
            for line in f.readlines():
                split = line.split()
                pair = (split[-1], split[0])

                # download ampr host file only during first iteration
                if not self.ampr_hosts:
                    self.get_ampr_hosts()

                if pair in self.ampr_hosts:
                    # exists, skipping
                    continue

                # TODO: delete stale records

                to_ampr.append(line)

        if to_ampr:
            send_mail('HamWAN DNS update', ''.join(set(to_ampr)),
                AMPR_DNS_FROM, [AMPR_DNS_TO], fail_silently=False)

        with open(AMPR_DNS_QUEUE, 'w') as f:
            f.write("")

    def get_ampr_hosts(self):
        # ftp://hamradio.ucsd.edu/pub/amprhosts
        self.ampr_hosts = []
        response = urllib2.urlopen('ftp://hamradio.ucsd.edu/pub/amprhosts')
        for line in response.readlines():
            split = line.split()
            if split:
                try:
                    self.ampr_hosts.append((split[0], split[2]))
                except:
                    print split
                    raise
