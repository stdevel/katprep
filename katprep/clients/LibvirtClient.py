#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class for sending requests to libvirt
"""

import libvirt
import logging



class SessionException(Exception):
    """
    Dummy class for session errors

.. class:: SessionException
    """
    pass



class LibvirtClient:
    """
    Class for communicating with libvirt

.. class:: LibvirtClient
    """
    LOGGER = logging.getLogger('LibvirtClient')
    """
    logging: Logger instance
    """
    URI = ""
    """
    str: libvirt URI
    """
    SESSION = None
    """
    session: libvirt session
    """

    def __init__(self, log_level, uri, username, password):
        """
        Constructor, creating the class. It requires specifying a URI and
        a username and password for communicating with the hypervisor.
        The constructor will throw an exception if an invalid libvirt URI
        was specified. After initialization, a connection is established
        automatically.

        :param log_level: log level
        :type log_level: logging
        :param uri: libvirt URI
        :type uri: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        #set logging
        self.LOGGER.setLevel(log_level)
        #validate and set URI
        if self.validate_uri(uri):
            self.URI = uri
        else:
            raise SessionException("Invalid URI string specified!")
        #set connection details and connect
        self.USERNAME = username
        self.PASSWORD = password
        self.__connect()



    @staticmethod
    def validate_uri(uri):
        """
        Verifies a libvirt URI and throws an exception if the URI is invalid.
        This is done by checking if the URI contains one of the well-known
        libvirt protocols.

        :param uri: a libvirt URI
        :type uri: str
        """
        prefixes = {
            "lxc", "qemu", "xen", "hyperv", "vbox", "openvz", "uml", "phyp",
            "vz", "bhyve", "esx", "vpx", "vmwareplayer", "vmwarews",
            "vmwarefusion"
        }
        #check whether a valid prefix was found
        for prefix in prefixes:
            if prefix in uri and "://" in uri:
                return True
        return False



    def __connect(self):
        """This function establishes a connection to the hypervisor."""
        #create weirdo auth dict
        auth = [
            [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
            self.retrieve_credentials, None
            ]
        #authenticate
        self.SESSION = libvirt.openAuth(self.URI, auth, 0)
        if self.SESSION == None:
            raise SessionException("Unable to establish connection to hypervisor!")



    def retrieve_credentials(self, credentials, user_data):
        """
        Retrieves the libvirt credentials in a strange format and hand it to
        the API in order to communicate with the hypervisor.
        To be honest, I have no idea why this has to be done this way. I have
        taken this function from the official libvirt documentation.

        :param credentials: libvirt credentials object
        :param user_data: some data that will never be used
        :type user_data: None
        """
        #get credentials for libvirt
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = self.USERNAME
                if len(credential[4]) == 0:
                    credential[4] = credential[3]
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = self.PASSWORD
            else:
                return -1
        return 0



    def __manage_snapshot(
            self, vm_name, snapshot_title, snapshot_text, action="create"
        ):
        """
        Creates/removes a snapshot for a particular virtual machine.
        This requires specifying a VM, comment title and text.
        There are also two alias functions.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Snapshot text
        :type snapshot_text: str
        :param remove_snapshot: Removes a snapshot if set to True
        :type remove_snapshot: bool

        """

        try:
            target_vm = self.SESSION.lookupByName(vm_name)
            if action.lower() == "remove":
                #remove snapshot
                target_snap = target_vm.snapshotLookupByName(snapshot_title, 0)
                return target_snap.delete(0)
            elif action.lower() == "revert":
                #revert snapshot
                target_snap = target_vm.snapshotLookupByName(snapshot_title, 0)
                return target_vm.revertToSnapshot(target_snap)
            else:
                #create snapshot
                snap_xml = """<domainsnapshot><name>{}</name><description>{}
                    "</description></domainsnapshot>""".format(
                        snapshot_title, snapshot_text
                    )
                return target_vm.snapshotCreateXML(snap_xml, 0)
        except libvirt.libvirtError as err:
            raise SessionException("Unable to {} snapshot: '{}'".format(
                action.lower(), err)
            )



    #Aliases
    def create_snapshot(self, vm_name, snapshot_title, snapshot_text):
        """
        Creates a snapshot for a particular virtual machine.
        This requires specifying a VM, comment title and text.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Snapshot text
        :type snapshot_text: str
        """
        return self.__manage_snapshot(vm_name, snapshot_title, snapshot_text)

    def remove_snapshot(self, vm_name, snapshot_title):
        """
        Removes a snapshot for a particular virtual machine.
        This requires specifying a VM and a comment title.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        return self.__manage_snapshot(
            vm_name, snapshot_title, "", action="remove"
        )

    def revert_snapshot(self, vm_name, snapshot_title):
        """
        Reverts to  a snapshot for a particular virtual machine.
        This requires specifying a VM and a comment title.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        return self.__manage_snapshot(
            vm_name, snapshot_title, "", action="revert"
        )



    def has_snapshot(self, vm_name, snapshot_title):
        """
        Returns whether a particular virtual machine is currently protected
        by a snapshot. This requires specifying a VM name.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        try:
            #find VM and get all snapshots
            target_vm = self.SESSION.lookupByName(vm_name)
            target_snapshots = target_vm.snapshotListNames(0)
            if snapshot_title in target_snapshots:
                return True
        except libvirt.libvirtError as err:
            self.LOGGER.error("Unable to determine snapshot: '{}'".format(err))
            raise SessionException(err)
        except Exception as err:
            raise SessionException(err)



    def get_vm_ips(self):
        """
        Returns a list of VMs and their IPs available through the current 
        connection.
        """
        try:
            #get all VMs
            vms = self.SESSION.listDefinedDomains()
            result = []

            #scan _all_ the VMs
            for vm in vms:
                #get VM and lookup hostname
                target_vm = self.SESSION.lookupByName(vm)
                target_hostname = target_vm.hostname()
                #lookup IP
                #TODO: IPv6 only?
                target_ip = socket.gethostbyname(target_hostname)
                result.append(
                    {"hostname": target_hostname, "ip": target_ip}
                )
            return result
        except libvirt.libvirtError as err:
            raise SessionException("Unable to get VM IP information: '{}'".format(err))



    def get_vm_hosts(self):
        """
        Returns a list of VMs and their hypervisors available through the
        current connection.
        """
        print "TODO: get_vm_hosts"



    def restart_vm(self, vm_name, force=False):
        """
        Restarts a particular VM (default: soft reboot using guest tools).

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param force: Flag whether a hard reboot is requested
        :type force: bool
        """
        try:
            target_vm = self.SESSION.lookupByName(vm_name)
            if force:
                #kill it with fire
                target_vm.reboot(1)
            else:
                #killing me softly
                target_vm.reboot(0)
        except libvirt.libvirtError as err:
            if "unsupported flags" in err.message.lower():
                #trying hypervisor default
                target_vm.reboot(0)
                self.LOGGER.error(
                    "Forcing reboot impossible, trying hypervisor default")
            else:
                raise SessionException("Unable to restart VM: '{}'".format(err))



    def powerstate_vm(self, vm_name):
        """
        Returns the power state of a particular virtual machine.

        :param vm_name: Name of a virtual machine
        :type vm_name: str

        """
        print "TODO: powerstate_vm"



    def __manage_power(
            self, vm_name, action="poweroff"
        ):
        """
        Powers a particual virtual machine on/off forcefully.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param action: action (poweroff, poweron)
        :type action: str

        """
        print "TODO: manage_power"



    #Aliases
    def poweroff_vm(self, vm_name):
        """
        Turns off a particual virtual machine forcefully.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        """
        return self.__manage_power(
            vm_name
        )

    def poweron_vm(self, vm_name):
        """
        Turns on a particual virtual machine forecully.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        """
        return self.__manage_power(
            vm_name, action="poweron"
        )
