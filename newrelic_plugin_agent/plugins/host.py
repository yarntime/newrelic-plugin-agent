"""
Host Performance Support

"""
import datetime
import logging
import psutil

from newrelic_plugin_agent.plugins import base

LOGGER = logging.getLogger(__name__)


class Host(base.Plugin):

    GUID = 'com.skyform.newrelic_host_plugin_agent'

    METRICS = ['host.cpu.utilization',
               'host.mem.utilization',
               'host.mem.total',
               'host.mem.available',
               'host.disk.utilization',
               'host.disk.total',
               'host.disk.available',
               'host.disk.partition.0', # for partition nubmer.
               # concrate partion should start from 'partition.1.[io.byte_send | io.byte_recv ]
               'host.disk.io.byte_read',
               'host.disk.io.byte_write',
               'host.net.io.byte_send',
               'host.net.io.byte_recv',
               'host.net.io.dropout',
               'host.net.interface.0' # for network interface number.
               # concrate network interface start from 'interface.1.[io.byte_send | io.byte_recv | io.error]
           ]
    
    def add_datapoints(self):
        """Add all of the data points for host
        
        :param str name: The name of the 
        """
        
        # CPU metrics
        self.add_gauge_value('host.cpu.utilization', None, psutil.cpu_percent())
        
        # MEM metric
        mem = psutil.phymem_usage()
        self.add_gauge_value('host.mem.utilization', None, mem.percent)
        self.add_gauge_value('host.mem.total', None, mem.total)
        self.add_gauge_value('host.mem.available', None, mem.available)

        # DISK metric
        parts = psutil.disk_partitions()
        disk = lambda:None
        setattr(disk, 'utilization', 0)
        setattr(disk, 'total', 0)
        setattr(disk, 'available', 0)

        partition_number = 0
        for part in parts:
            pusage = psutil.disk_usage(part.mountpoint)
            disk.total += pusage.total
            disk.available += pusage.free
            disk.utilization += pusage.percent
            partition_number += 1

            self.add_gauge_value('host.disk.partition.%s.utilization' % partition_number, None,
                                 pusage.percent)
            self.add_gauge_value('host.disk.partition.%s.total' % partition_number, None,
                                 pusage.total)
            self.add_gauge_value('host.disk.partition.%s.available' % partition_number, None,
                                 pusage.free)

        disk.utilization = disk.utilization / partition_number
        
        self.add_gauge_value('host.disk.utilization', None, disk.utilization)
        self.add_gauge_value('host.disk.total', None, disk.total)
        self.add_gauge_value('host.disk.available', None, disk.available)
        self.add_gauge_value('host.disk.partition.0', None, partition_number)

        diskio = psutil.disk_io_counters(perdisk=False)
        self.add_gauge_value('host.disk.io.byte_read', None, diskio.read_bytes)
        self.add_gauge_value('host.disk.io.byte_write', None, diskio.write_bytes)

        # NET metric
        netio = psutil.net_io_counters(pernic=False)
        self.add_gauge_value('host.net.io.byte_send', None, netio.bytes_sent)
        self.add_gauge_value('host.net.io.byte_recv', None, netio.bytes_recv)
        self.add_gauge_value('host.net.io.dropout', None, netio.dropout)

        nicnum = 0
        nicsio = psutil.net_io_counters(pernic=True)
        for nic in nicsio.keys():
            if nic == 'lo': continue
            nicio = nicsio[nic]

            nicnum += 1
            self.add_gauge_value('host.net.nic.%s.byte_send' % nicnum, None, nicio.bytes_sent)
            self.add_gauge_value('host.net.nic.%s.byte_recv' % nicnum, None, nicio.bytes_recv)
            self.add_gauge_value('host.net.nic.%s.dropout' % nicnum, None, nicio.dropout)

        self.add_gauge_value('host.net.nic.0', None, nicnum)

        #DONE

    def poll(self):
        """Poll HTTP server for stats data"""
        self.initialize()
        self.add_datapoints()
        
