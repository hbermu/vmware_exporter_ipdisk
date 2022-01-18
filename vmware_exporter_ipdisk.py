# !/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
# autopep8'd
"""
Handles collection of IPs and Disks metrics for vmware.
"""
# Generic imports
import argparse
import logging
import requests
import time
import yaml

# Prometheus imports
from prometheus_client import start_http_server, Gauge

# vSphere imports
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl, vim
import atexit

"""
disable annoying urllib3 warning messages for connecting to servers with non verified certificate Doh!
"""
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from __init__ import __version__


class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, config, polling_interval_seconds=30):
        self.config = config
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.vmware_vm_net_ip = Gauge('vmware_vm_net_ip', 'IP of the VM',
                                      labelnames=['vm_name', 'vm_ip'])
        self.vmware_vm_disk = Gauge('vmware_vm_disk_size', 'Size in bytes of the attached disk',
                                    labelnames=['vm_name', 'vm_disk_index'])

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        service_instance = None
        logging.info("Trying to connect {vSphere_host}:{vSphere_port} vSphere with user {vSphere_user}."
                     .format(vSphere_host=self.config["vsphere_host"], vSphere_port=self.config["vsphere_port"],
                             vSphere_user=self.config["vsphere_user"]))
        try:
            if self.config["ignore_ssl"]:
                service_instance = SmartConnect(host=self.config["vsphere_host"],
                                                user=self.config["vsphere_user"],
                                                pwd=self.config["vsphere_password"],
                                                port=self.config["vsphere_port"],
                                                disableSslCertValidation=True)
            else:
                service_instance = SmartConnect(host=self.config["vsphere_host"],
                                                user=self.config["vsphere_user"],
                                                pwd=self.config["vsphere_password"],
                                                port=self.config["vsphere_port"])

        except IOError as io_error:
            logging.info("Error connecting: {error}".format(error=io_error))
            raise SystemExit("Error connecting.")
        if not service_instance:
            logging.info("Unable to connect to host with supplied credentials.")
            raise SystemExit("Unable to connect to host with supplied credentials.")
        atexit.register(Disconnect, service_instance)

        try:
            content = service_instance.RetrieveContent()
            logging.debug("Starting point to look into: {rootFolder}.".format(rootFolder=content.rootFolder))
            container = content.rootFolder
            logging.debug("Object types to look for: VirtualMachine.")
            view_type = [vim.VirtualMachine]
            recursive = True
            logging.debug("Getting all VMs.")
            container_view = content.viewManager.CreateContainerView(
                container, view_type, recursive)

            children = container_view.view
            logging.info("Getting through the entire VMs list")
            for child in children:
                logging.debug("Working with VM: {vm}.".format(vm=child.summary.config.name))
                logging.debug("Getting IPs")
                if child.summary.guest is not None and child.summary.guest.ipAddress is not None:
                    for nic in child.guest.net:
                        addresses = nic.ipConfig.ipAddress
                        for adr in addresses:
                            self.vmware_vm_net_ip.labels(vm_name=child.summary.config.name,
                                                         vm_ip=str(adr.ipAddress) + "/" + str(adr.prefixLength)).set(1)
                logging.debug("Disks")
                for device in child.config.hardware.device:
                    if 2000 <= device.key <= 2100:
                        disk_index = str(device.deviceInfo.label).split(" ")[-1]
                        disk_size = int(str(device.deviceInfo.summary.split(" ")[0].replace(",", "")))*1000
                        self.vmware_vm_disk.labels(vm_name=child.summary.config.name,
                                                   vm_disk_index=disk_index).set(disk_size)

            logging.debug("All VMs metrics added.")

        except vmodl.MethodFault as error:
            logging.info("Caught vmodl fault: {error}.".format(error=error))
            raise SystemExit("Caught vmodl fault.")


def main():
    """ start up twisted reactor """
    parser = argparse.ArgumentParser(description='VMWare IPs and Disks metrics exporter for Prometheus')
    parser.add_argument('-c', '--config', dest='config_file',
                        default="config.yml", help="configuration file")
    parser.add_argument('-a', '--address', dest='address', type=str,
                        default='0.0.0.0', help="HTTP address to expose metrics")
    parser.add_argument('-p', '--port', dest='port', type=int,
                        default=9372, help="HTTP port to expose metrics")
    parser.add_argument('-t', '--time', dest='time', type=int,
                        default=1, help="Time in seconds between get VMWare values")
    parser.add_argument('-l', '--loglevel', dest='loglevel',
                        default="INFO", help="Set application loglevel INFO, DEBUG")
    parser.add_argument('-v', '--version', action="version",
                        version='vmware_exporter_ipdisk {version}'.format(version=__version__),
                        help='Print version and exit')

    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {level}".format(level=args.loglevel))
    logging.basicConfig(level=numeric_level, format='%(asctime)s %(levelname)s:%(message)s')
    logging.debug("CAREFUL! Using debug option will print passwords.")

    logging.info("Reading config file {config}.".format(config=args.config_file))
    with open(args.config_file) as file:
        config_list = yaml.load(file, Loader=yaml.FullLoader)
        logging.debug("Working with config: {config}".format(config=config_list))

    app_metrics = AppMetrics(
        config=config_list,
        polling_interval_seconds=int(args.time)
    )

    logging.info("Starting web server on port {address}:{port}.".format(address=args.address, port=args.port))
    start_http_server(int(args.port), addr=args.address)
    app_metrics.run_metrics_loop()


if __name__ == '__main__':
    main()
