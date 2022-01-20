# vmware_exporter_ipdisk

VMware vCenter Exporter for Prometheus. 

Get VMware vCenter information:
- VMs IPs
- VMs Disks and Size
- VMs hostnames

## Usage

*Requires Python >= 3.8*
*Requires [VMware Tools](https://docs.vmware.com/en/VMware-Tools/index.html) installed on VM*

- Install requirements with `$python3 -m pip install -r requirements.txt`
- Run `$ python3 vmware_exporter_ipdisk.py`
- Go to http://localhost:9372/

#### Docker
You can run the exporter with docker:
```
docker run -p 9372:9372 -v config.yml:/vmware_exporter_ipdisk/config.yml hbermu/vmware_exporter_ipdisk
```

### Configuration
If you do plan to use a configuration file different from `./config.yml`, be sure to override the container entrypoint with -c path/to/your/config.yml to the command arguments.

## References

The VMware exporter uses these libraries:
- [pyVmomi](https://github.com/vmware/pyvmomi) for VMware connection
- Prometheus [client_python](https://github.com/prometheus/client_python) for Prometheus supervision

The initial code is mainly inspired by:
- https://github.com/pryorda/vmware_exporter (I tried to add this functionality to his code, but was impossible for me)

# Maintainer

Hector Bermudez [hbermu](https://github.com/hbermu)
