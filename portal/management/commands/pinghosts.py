from threading import Thread
import subprocess
from Queue import Queue

from django.core.management.base import BaseCommand, CommandError
from portal.models import IPAddress

class Command(BaseCommand):
    help = 'ICMP pings all hosts'

    def handle(self, *args, **options):
        num_threads = 4
        queue = Queue()

        # Spawn thread pool
        for i in range(num_threads):
            worker = Thread(target=self.pinger, args=(i, queue))
            worker.setDaemon(True)
            worker.start()
        # Place work in queue
        for ip in IPAddress.objects.all():
            queue.put(ip)
        # Wait until worker threads are done to exit
        try:
            queue.join()
        except KeyboardInterrupt:
            pass

    def pinger(self, i, q):
        """Pings ipaddress"""
        while True:
            ip = q.get()
            label = '%s %s' % (str(ip.ip).ljust(16), ip.fqdn())
            if ip.ping():
                self.stdout.write('UP   %s' % label)
            else:
                self.stdout.write('DOWN %s' % label)
            q.task_done()
