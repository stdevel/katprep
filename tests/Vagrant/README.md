# Vagrant boxes

This folder contains Vagrant boxes for suitable for testing integration during development.

## Network

Every box forwards some ports directly so that you can use the endpoints for unit tests.

## Boxes

| Box | Autostart | Description | Forwarded ports |
| --- | --------- | ----------- | --------------- |
| ``monitoring`` | yes | EL7 running OMD with Icinga2, etc. | 80=>8080 (*http*), 443=>8443 (*https*), 5665=>8665 (*icinga2*) |
| ``zabbix`` | no | EL7 running Zabbix | 80=>8081 (*http*), 443=>8444 (*https*) |
| ``xen`` | no | EL7 running XEN and dummy VM with networking (**WIP**) | |
| ``kvm`` | yes | EL7 running KVM and dummy VM with networking (**WIP**) | |
| ``esxi`` | no | vSphere ESXi 6.7 running a dummy VM with networking (**WIP**) | |
| ``katello`` | yes | EL7 running Foreman/Katello (**WIP**) | 80=>8083 (*http*), 443=>8446 (*https*) |
| ``uyuni`` | yes | openSUSE 15.1 running Uyuni | 80=>8084 (*http*), 443=>8447 (*https*) |

## Requirements

- Hardware
  - at least 16 GB of memory for running the VMs
  - at least 20 GB of disk storage
- Software
  - [HashiCorp Vagrant](https://vagrantup.com)
  - [Oracle VirtualBox](https://virtualbox.org)

## Usage

Run the following command to create all autostart boxes:

```bash
$ vagrant up
```

To create non-autostart boxes, run one of the following commands:

```bash
$ vagrant up zabbix
$ vagrant up xen
$ vagrant up esxi
```

To destroy the VMs after testing integrations, run the following command:

```bash
$ vagrant destroy
```

## Running tests in VMs

TODO: will follow soon
