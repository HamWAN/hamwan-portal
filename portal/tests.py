import unittest

from django.test import TestCase

from dns.models import Record
from portal.models import Host, IPAddress


class IPAddressTest(TestCase):
    fixtures = ['domains.json', 'example_host.json']

    def _assert_address_records(self, address, want=1):
        a_records = Record.objects.filter(type="A", content=str(address.ip))
        self.assertEqual(want, a_records.count())
        if want:
            self.assertEqual(address.fqdn(), a_records[0].name)
        ptr_record = Record.objects.filter(
            type="PTR", content=str(address.fqdn()))
        self.assertEqual(want, ptr_record.count())

    def test_create_address(self):
        host = Host.objects.get(name="s1.seattle")
        ip = IPAddress(host=host, interface="wlan2", ip="44.25.2.2")
        ip.save()
        self._assert_address_records(ip)

    @unittest.skip("update is broken")
    def test_update_address(self):
        old_addr = "44.25.0.1"
        new_addr = "44.25.0.2"
        address = IPAddress.objects.get(ip=old_addr)
        address.ip = new_addr
        address.save()
        self._assert_address_records(
            IPAddress(ip=new_addr, host=address.host, interface=address.interface), want=1)
        self._assert_address_records(
            IPAddress(ip=old_addr, host=address.host, interface=address.interface), want=0)

    def test_delete_address(self):
        old_addr = "44.25.0.1"
        address = IPAddress.objects.get(ip=old_addr)
        address.delete()
        self._assert_address_records(address, want=0)

    def test_rename_host(self):
        host = Host.objects.get(name="s1.seattle")
        host.name = "s2.seattle"
        host.save()

        cname_records = Record.objects.filter(type="CNAME")
        self.assertEqual(1, cname_records.count())
        self.assertEqual(host.fqdn(), cname_records[0].name)
        self.assertEqual("loopback.s2.seattle.hamwan.net",
                         cname_records[0].content)

        addresses = IPAddress.objects.filter(host=host)
        self.assertEqual(3, addresses.count())
        for addr in addresses:
            self._assert_address_records(addr)
