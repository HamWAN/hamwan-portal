from ipaddr import IPNetwork

from django.core.management.base import BaseCommand, CommandError
from portal.models import Subnet


prefixlenq = Subnet.objects.extra(select={'masklen': "masklen(network)"}
    ).extra(order_by=['masklen'])


def get_next_network(address, prefixlen):
    return IPNetwork("/".join(map(str, [address, prefixlen])))


def find_free_network(existing_networks, start, prefixlen):
    new_network = get_next_network(start, prefixlen)
    for net in existing_networks:
        if new_network in net or net in new_network:
            return find_free_network(existing_networks,
                                     max(new_network) + 1,
                                     prefixlen)
    return new_network


class Command(BaseCommand):
    args = '<block name> <prefix length>'
    help = 'Prints the next available subnet in the specified block.\n' + \
           '\nSuggested block names:\n    ' + \
           '\n    '.join(prefixlenq.values_list('notes', flat=True)[:10]) + \
           '\nBlock names use case-insensitive starts-with matching.'

    def handle(self, *args, **options):
        blockname, prefixlen = args
        try:
            block = prefixlenq.filter(notes__istartswith=blockname)[0].network
        except IndexError:
            raise CommandError(
                "Block starting with '%s' not found." % blockname)
        found = find_free_network(
            [n.network for n in Subnet.objects.extra(
                where=["inet '%s' >> network" % block])],
            min(block),
            prefixlen)
        if found not in block:
            raise CommandError(
                "No /%ss available in %s" % (prefixlen, str(block)))
        return str(found)
