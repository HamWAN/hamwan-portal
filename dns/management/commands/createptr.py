from django.core.management.base import BaseCommand, CommandError
from dns.models import Record, Domain
from portal.network import reverse
from ipaddr import IPAddress, IPNetwork
from config.settings import ROOT_DOMAIN, DEFAULT_NETWORK

class Command(BaseCommand):
    args = '<network> <pattern>'
    defaultnetwork = IPNetwork(DEFAULT_NETWORK)
    defaultpattern = f'%(0)s-%(1)s-%(2)s-%(3)s.ip.{ROOT_DOMAIN}'
    help = 'Creates a PTR for all IPs without a current PTR.\n\n' \
           'The default pattern is: %s' % defaultpattern

    def handle(self, *args, **options):
        if len(args) == 0:
            network, pattern = self.defaultnetwork, self.defaultpattern
        if len(args) == 1:
            network, pattern = IPNetwork(args[0]), self.defaultpattern
        if len(args) == 2:
            network, pattern = IPNetwork(args[0]), args[1]

        for ip in network.iterhosts():
            name = reverse(ip)
            content = pattern % dict(
                [(str(k), v) for k, v in enumerate(str(ip).split('.'))])

            # print "%s\tcreated: %s" % (
            #     Record.objects.get_or_create(domain=self.get_domain(content),
            #         name=content, type='A', defaults={'content': str(ip)}))
            print "%s\t\tcreated: %s" % (
                Record.objects.get_or_create(domain=self.get_domain(name),
                    name=name, type='PTR', defaults={'content': content}))

    def get_domain(self, name):
        if not hasattr(self, 'domains'):
            self.domains = {}
            for domain in Domain.objects.all():
                self.domains[domain.name] = domain

        for (k, v) in self.domains.items():
            if name.endswith(k):
                return v
