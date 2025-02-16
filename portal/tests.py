import unittest

from django.urls import reverse
from django.test import TestCase

from dns.models import Record
from portal.models import Host, IPAddress
from portal import views


class AnsibleHostsTest(TestCase):
    fixtures = ['domains.json', 'example_host.json']

    def test_ansible_hosts_view(self):
        response = self.client.get(reverse(views.ansible_hosts))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"name_s1.seattle": ["s1.seattle.hamwan.net"], "os_": ["s1.seattle.hamwan.net"], "type_sector": ["s1.seattle.hamwan.net"], "_meta": {"hostvars": {}}, "owner_": ["s1.seattle.hamwan.net"]}')


class IPAddressTest(TestCase):
    fixtures = ['domains.json', 'example_host.json']

    def _assert_address_records(self, address, want=1):
        a_records = Record.objects.filter(type="A", content=str(address.ip))
        self.assertEqual(want, a_records.count())
        if want:
            self.assertEqual(address.fqdn(), a_records[0].name)
        ptr_record = Record.objects.filter(
            type="PTR", name=address._generate_ptr())
        self.assertEqual(want, ptr_record.count())

    def test_create_address(self):
        host = Host.objects.get(name="s1.seattle")
        ip = IPAddress(host=host, interface="wlan2", ip="44.25.2.2")
        ip.save()
        self._assert_address_records(ip)

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

    def test_delete_host(self):
        host = Host.objects.get(name="s1.seattle")
        host.delete()
        for model in Host, IPAddress, Record:
            self.assertFalse(model.objects.count(),
                             msg="orphaned objects: {}".format(model.objects.all()))
