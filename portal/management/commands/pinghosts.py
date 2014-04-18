from threading import Thread
import subprocess
from Queue import Queue

from django.core.management.base import BaseCommand, CommandError
from portal.models import Host

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
        for host in Host.objects.all():
            queue.put(host)
        # Wait until worker threads are done to exit    
        queue.join()

    def pinger(self, i, q):
        """Pings host"""
        while True:
            host = q.get()
            if host.ping():
                self.stdout.write('%s UP' % host)
            else:
                self.stdout.write('%s DOWN' % host)
            q.task_done()
