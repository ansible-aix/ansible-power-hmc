#!/usr/bin/python

# Copyright: (c) 2018- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: powervm_lpar_instance
author:
    - Anil Vijayan (@AnilVijayan)
    - Navinakumar Kandakur (@nkandak1)
short_description: Create, Delete and shutdown an AIX/Linux or IBMi partition
notes:
    - Currently supports creation of partition (powervm instance) with only processor and memory settings on dedicated mode
description:
    - "Creates AIX/Linux or IBMi partition with specified configuration details on mentioned system"
    - "Or Deletes specified AIX/Linux or IBMi partition on specified system"
    - "Or Shutdown specified AIX/Linux or IBMi partition on specified system"
    - "Or Poweron specified AIX/Linux or IBMi partition with specified configuration details on specified system"

version_added: "1.1.0"
requirements:
- Python >= 3
options:
    hmc_host:
        description:
            - The ipaddress or hostname of HMC
        required: true
        type: str
    hmc_auth:
        description:
            - Username and Password credential of HMC
        required: true
        type: dict
        suboptions:
            username:
                description:
                    - HMC user name
                required: true
                type: str
            password:
                description:
                    - HMC password
                required: true
                type: str
    system_name:
        description:
            - The name of the managed system
        required: true
        type: str
    vm_name:
        description:
            - The name of the powervm partition to create/delete
        required: true
        type: str
    proc:
        description:
            - The number of dedicated processors to create partition.
            - Default value is 2.
        type: int
    mem:
        description:
            - The value of dedicated memory value in megabytes to create partition.
            - Default value is 2048 MB.
        type: int
    os_type:
        description:
            - Type of logical partition to be created
            - C(aix_linux) or C(linux) or C(aix) for AIX or Linux operating system
            - C(ibmi) for IBMi operating system
        type: str
        choices: ['aix','linux','aix_linux','ibmi']
    prof_name:
        description:
            - Partition profile needs to be used to activate
            - If user doesn't pass this option, current configureation profile will be considered
        type: str
    keylock:
        description:
            - The keylock position to set.
            - If user doesn't provide this option, current settings of this option in partition will be considered.
        type: str
        choices: ['manual', 'norm']
    iIPLsource:
        description:
            - The inital program load (IPL) source to use when activating an IBMi partition.
            - If user doesn't provide this option, current setting of this option in partition will be considered.
            - If this option provided to AIX/Linux type partition, operation gives a warning and then ignores this option and proceed with operation.
        type: str
        choices: ['a','b','c','d']
    state:
        description:
            - C(present) creates a partition of specifed I(os_type), I(vm_name), I(proc) and I(memory) on specified I(system_name)
            - C(absent) deletes a partition of specified I(vm_name) on specified I(system_name)
        required: true
        type: str
        choices: ['present', 'absent']
    action:
        description:
            - C(shutdown) shutdown a partition of specified I(vm_name) on specified I(system_name)
            - C(poweron) poweron a partition of specified I(vm_name) with spefified I(prof_name), I(keylock), I(iIPLsource) on specified I(system_name)
'''

EXAMPLES = '''
- name: Create an IBMi logical partition instance
  powervm_lpar_instance:
      hmc_host: '{{ inventory_hostname }}'
      hmc_auth:
         username: '{{ ansible_user }}'
         password: '{{ hmc_password }}'
      system_name: <system_name>
      vm_name: <vm_name>
      proc: 4
      mem: 20480
      os_type: ibmi
      state: present

- name: Create an AIX/Linux logical partition instance with default proc and mem values
  powervm_lpar_instance:
      hmc_host: '{{ inventory_hostname }}'
      hmc_auth:
         username: '{{ ansible_user }}'
         password: '{{ hmc_password }}'
      system_name: <system_name>
      vm_name: <vm_name>
      os_type: aix_linux
      state: present

- name: Delete a logical partition instance
  powervm_lpar_instance:
      hmc_host: '{{ inventory_hostname }}'
      hmc_auth:
         username: '{{ ansible_user }}'
         password: '{{ hmc_password }}'
      system_name: <system_name>
      vm_name: <vm_name>
      state: absent

- name: Shutdown a logical partition
  powervm_lpar_instance:
      hmc_host: '{{ inventory_hostname }}'
      hmc_auth:
         username: '{{ ansible_user }}'
         password: '{{ hmc_password }}'
      system_name: <system_name>
      vm_name: <vm_name>
      action: shutdown

- name: Activate a AIX/Linux logical partition with user defined profile_name
  powervm_lpar_instance:
      hmc_host: '{{ inventory_hostname }}'
      hmc_auth:
         username: '{{ ansible_user }}'
         password: '{{ hmc_password }}'
      system_name: <system_name>
      vm_name: <vm_name>
      prof_name: <profile_name>
      action: poweron

- name: Activate a IBMi logical partition with user defined keylock and iIPLsource options
  powervm_lpar_instance:
      hmc_host: '{{ inventory_hostname }}'
      hmc_auth:
         username: '{{ ansible_user }}'
         password: '{{ hmc_password }}'
      system_name: <system_name>
      vm_name: <vm_name>
      keylock: 'norm'
      iIPLsource: 'd'
      action: poweron

'''

RETURN = '''
partition_info:
    description: The configuration of the partition after creation
    type: dict
    sample: {"AllocatedVirtualProcessors": null, "AssociatedManagedSystem": "<system-name>", "CurrentMemory": 1024, \
            "CurrentProcessingUnits": null, "CurrentProcessors": 1, "Description": null, "HasDedicatedProcessors": "true", \
            "HasPhysicalIO": "true", "IsVirtualServiceAttentionLEDOn": "false", "LastActivatedProfile": "default_profile", \
            "MemoryMode": "Dedicated", "MigrationState": "Not_Migrating", "OperatingSystemVersion": "Unknown", \
            "PartitionID": 11, "PartitionName": "<partition-name>", "PartitionState": "not activated", \
            "PartitionType": "AIX/Linux", "PowerManagementMode": null, "ProgressState": null, "RMCState": "inactive", \
            "ReferenceCode": "", "RemoteRestartState": "Invalid", "ResourceMonitoringIPAddress": null, "SharingMode": "sre idle proces"}
    returned: on success for state C(present)
'''

import sys
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_cli_client import HmcCliConnection
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_resource import Hmc
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_exceptions import HmcError
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_exceptions import ParameterError
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_exceptions import Error
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_rest_client import parse_error_response
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_rest_client import HmcRestClient
from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_rest_client import add_taggedIO_details
from random import randint
try:
    from lxml import etree
except ImportError:
    pass  # Handled by hmc rest client module

# Generic setting for log initializing and log rotation
import logging
LOG_FILENAME = "/tmp/ansible_power_hmc.log"
logger = logging.getLogger(__name__)


def init_logger():
    logging.basicConfig(
        filename=LOG_FILENAME,
        format='[%(asctime)s] %(levelname)s: [%(funcName)s] %(message)s',
        level=logging.DEBUG)


def validate_proc_mem(system_dom, proc, mem):

    curr_avail_proc_units = system_dom.xpath('//CurrentAvailableSystemProcessorUnits')[0].text
    int_avail_proc = int(float(curr_avail_proc_units))

    curr_avail_mem = system_dom.xpath('//CurrentAvailableSystemMemory')[0].text
    int_avail_mem = int(curr_avail_mem)
    curr_avail_lmb = system_dom.xpath('//CurrentLogicalMemoryBlockSize')[0].text
    lmb = int(curr_avail_lmb)

    if proc > int_avail_proc:
        raise HmcError("Available system proc units is not enough. Provide value on or below {0}".format(str(int_avail_proc)))

    if mem % lmb > 0:
        raise HmcError("Requested mem value not in mutiple of block size:{0}".format(curr_avail_lmb))

    if mem > int_avail_mem:
        raise HmcError("Available system memory is not enough. Provide value on or below {0}".format(curr_avail_mem))


def validate_parameters(params):
    '''Check that the input parameters satisfy the mutual exclusiveness of HMC'''
    opr = None
    if params['state'] is not None:
        opr = params['state']
    else:
        opr = params['action']

    if opr == 'present':
        mandatoryList = ['hmc_host', 'hmc_auth', 'system_name', 'vm_name', 'os_type']
        unsupportedList = ['prof_name', 'keylock', 'iIPLsource']
    elif opr == 'poweron':
        mandatoryList = ['hmc_host', 'hmc_auth', 'system_name', 'vm_name']
        unsupportedList = ['proc', 'mem', 'os_type']
    else:
        mandatoryList = ['hmc_host', 'hmc_auth', 'system_name', 'vm_name']
        unsupportedList = ['proc', 'mem', 'os_type', 'prof_name', 'keylock', 'iIPLsource']

    collate = []
    for eachMandatory in mandatoryList:
        if not params[eachMandatory]:
            collate.append(eachMandatory)
    if collate:
        if len(collate) == 1:
            raise ParameterError("mandatory parameter '%s' is missing" % (collate[0]))
        else:
            raise ParameterError("mandatory parameters '%s' are missing" % (','.join(collate)))

    collate = []
    for eachUnsupported in unsupportedList:
        if params[eachUnsupported]:
            collate.append(eachUnsupported)

    if collate:
        if len(collate) == 1:
            raise ParameterError("unsupported parameter: %s" % (collate[0]))
        else:
            raise ParameterError("unsupported parameters: %s" % (', '.join(collate)))


def create_partition(module, params):
    changed = False
    cli_conn = None
    rest_conn = None
    system_uuid = None
    server_dom = None
    validate_parameters(params)
    hmc_host = params['hmc_host']
    hmc_user = params['hmc_auth']['username']
    password = params['hmc_auth']['password']
    system_name = params['system_name']
    vm_name = params['vm_name']
    proc = str(params['proc'] or 2)
    mem = str(params['mem'] or 2048)
    os_type = params['os_type']
    temp_template_name = "draft_ansible_powervm_create_{0}".format(str(randint(1000, 9999)))
    temp_copied = False

    cli_conn = HmcCliConnection(module, hmc_host, hmc_user, password)
    hmc = Hmc(cli_conn)

    try:
        rest_conn = HmcRestClient(hmc_host, hmc_user, password)
    except Exception as error:
        error_msg = parse_error_response(error)
        module.fail_json(msg=error_msg)

    try:
        system_uuid, server_dom = rest_conn.getManagedSystem(system_name)
    except Exception as error:
        try:
            rest_conn.logoff()
        except Exception:
            logger.debug("Logoff error")
        error_msg = parse_error_response(error)
        module.fail_json(msg=error_msg)
    if not system_uuid:
        module.fail_json(msg="Given system is not present")

    try:
        partition_uuid, partition_dom = rest_conn.getLogicalPartition(system_uuid, vm_name)
    except Exception as error:
        try:
            rest_conn.logoff()
        except Exception:
            logger.debug("Logoff error")
        error_msg = parse_error_response(error)
        module.fail_json(msg=error_msg)

    if partition_dom:
        try:
            partition_prop = rest_conn.quickGetPartition(partition_uuid)
            partition_prop['AssociatedManagedSystem'] = system_name
        except Exception as error:
            try:
                rest_conn.logoff()
            except Exception:
                logger.debug("Logoff error")
            error_msg = parse_error_response(error)
            module.fail_json(msg=error_msg)
        return False, partition_prop

    validate_proc_mem(server_dom, int(proc), int(mem))

    try:
        if os_type in ['aix', 'linux', 'aix_linux']:
            reference_template = "QuickStart_lpar_rpa_2"
        else:
            reference_template = "QuickStart_lpar_IBMi_2"
        rest_conn.copyPartitionTemplate(reference_template, temp_template_name)
        temp_copied = True
        max_lpars = server_dom.xpath("//MaximumPartitions")[0].text
        next_lpar_id = hmc.getNextPartitionID(system_name, max_lpars)
        logger.debug("Next Partiion ID: %s", str(next_lpar_id))
        logger.debug("CEC uuid: %s", system_uuid)

        # On servers that do not support the IBM i partitions with native I/O capability
        if os_type == 'ibmi' and \
                server_dom.xpath("//IBMiNativeIOCapable") and \
                server_dom.xpath("//IBMiNativeIOCapable")[0].text == 'false':
            temporary_temp_dom = rest_conn.getPartitionTemplate(name=temp_template_name)
            temp_uuid = temporary_temp_dom.xpath("//AtomID")[0].text
            srrTag = temporary_temp_dom.xpath("//SimplifiedRemoteRestartEnable")[0]
            srrTag.addnext(etree.XML('<isRestrictedIOPartition kb="CUD" kxe="false">true</isRestrictedIOPartition>'))
            rest_conn.updatePartitionTemplate(temp_uuid, temporary_temp_dom)

        resp = rest_conn.checkPartitionTemplate(temp_template_name, system_uuid)
        draft_uuid = resp.xpath("//ParameterName[text()='TEMPLATE_UUID']/following-sibling::ParameterValue")[0].text
        draft_template_xml = rest_conn.getPartitionTemplate(uuid=draft_uuid)
        if not draft_template_xml:
            module.fail_json(msg="Not able to fetch template for partition deploy")

        config_dict = {'lpar_id': str(next_lpar_id)}
        config_dict['vm_name'] = vm_name
        config_dict['proc'] = proc
        config_dict['mem'] = mem
        if os_type == 'ibmi':
            add_taggedIO_details(draft_template_xml)

        rest_conn.updatePartitionTemplate(draft_uuid, draft_template_xml, config_dict)
        rest_conn.transformPartitionTemplate(draft_uuid, system_uuid)
        resp_dom = rest_conn.deployPartitionTemplate(draft_uuid, system_uuid)
        partition_uuid = resp_dom.xpath("//ParameterName[text()='PartitionUuid']/following-sibling::ParameterValue")[0].text
        partition_prop = rest_conn.quickGetPartition(partition_uuid)
        partition_prop['AssociatedManagedSystem'] = system_name
        changed = True
    except Exception as error:
        error_msg = parse_error_response(error)
        logger.debug("Line number: %d exception: %s", sys.exc_info()[2].tb_lineno, repr(error))
        module.fail_json(msg=error_msg)
    finally:
        if temp_copied:
            try:
                rest_conn.deletePartitionTemplate(temp_template_name)
            except Exception as del_error:
                error_msg = parse_error_response(del_error)
                logger.debug(error_msg)

        try:
            rest_conn.logoff()
        except Exception as logoff_error:
            error_msg = parse_error_response(logoff_error)
            logger.debug(error_msg)

    return changed, partition_prop


def remove_partition(module, params):
    changed = False
    rest_conn = None
    system_uuid = None
    validate_parameters(params)
    hmc_host = params['hmc_host']
    hmc_user = params['hmc_auth']['username']
    password = params['hmc_auth']['password']
    system_name = params['system_name']
    vm_name = params['vm_name']

    try:
        rest_conn = HmcRestClient(hmc_host, hmc_user, password)
    except Exception as error:
        logger.debug(repr(error))
        module.fail_json(msg="Logon to HMC failed")

    try:
        system_uuid, server_dom = rest_conn.getManagedSystem(system_name)
    except Exception as error:
        try:
            rest_conn.logoff()
        except Exception:
            logger.debug("Logoff error")
        error_msg = parse_error_response(error)
        module.fail_json(msg=error_msg)
    if not system_uuid:
        module.fail_json(msg="Given system is not present")

    try:
        partition_uuid, partition_dom = rest_conn.getLogicalPartition(system_uuid, vm_name)
        if not partition_dom:
            logger.debug("Given partition already absent on the managed system")
            return False, None

        if partition_dom.xpath("//PartitionState")[0].text != 'not activated':
            module.fail_json(msg="Given logical partition:{0} is not in shutdown state".format(vm_name))

        rest_conn.deleteLogicalPartition(partition_uuid)
        changed = True
    except Exception as error:
        error_msg = parse_error_response(error)
        logger.debug("Line number: %d exception: %s", sys.exc_info()[2].tb_lineno, repr(error))
        module.fail_json(msg=error_msg)
    finally:
        try:
            rest_conn.logoff()
        except Exception as logoff_error:
            error_msg = parse_error_response(logoff_error)
            module.warn(error_msg)

    return changed, None


def poweroff_partition(module, params):
    changed = False
    rest_conn = None
    system_uuid = None
    lpar_uuid = None
    validate_parameters(params)
    hmc_host = params['hmc_host']
    hmc_user = params['hmc_auth']['username']
    password = params['hmc_auth']['password']
    system_name = params['system_name']
    vm_name = params['vm_name']

    try:
        rest_conn = HmcRestClient(hmc_host, hmc_user, password)
    except Exception as error:
        logger.debug(repr(error))
        module.fail_json(msg="Logon to HMC failed")

    try:
        system_uuid, server_dom = rest_conn.getManagedSystem(system_name)
        if not system_uuid:
            module.fail_json(msg="Given system is not present")

        lpar_response = rest_conn.getLogicalPartitionsQuick(system_uuid)
        if lpar_response:
            lpar_quick_list = json.loads(rest_conn.getLogicalPartitionsQuick(system_uuid))

        if lpar_quick_list:
            for eachLpar in lpar_quick_list:
                if eachLpar['PartitionName'] == vm_name:
                    partition_dict = eachLpar
                    lpar_uuid = eachLpar['UUID']
                    break

        if not lpar_uuid:
            module.fail_json(msg="Given Logical Partition is not present on given system")

        partition_state = partition_dict["PartitionState"]

        if partition_state == 'not activated':
            logger.debug("Given partition already in not activated state")
            return False, None
        else:
            resp_dom = rest_conn.poweroffPartition(lpar_uuid, 'shutdown')
            return_code = resp_dom.xpath("//ParameterName[text()='returnCode']/following-sibling::ParameterValue")[0].text
            if return_code == '0':
                changed = True
            else:
                resp_result = resp_dom.xpath("//ParameterName[text()='result']/following-sibling::ParameterValue")[0].text
                module.fail_json(msg=resp_result)

    except Exception as error:
        error_msg = parse_error_response(error)
        logger.debug("Line number: %d exception: %s", sys.exc_info()[2].tb_lineno, repr(error))
        module.fail_json(msg=error_msg)
    finally:
        try:
            rest_conn.logoff()
        except Exception as logoff_error:
            error_msg = parse_error_response(logoff_error)
            module.warn(error_msg)

    return changed, None


def poweron_partition(module, params):
    changed = False
    rest_conn = None
    system_uuid = None
    lpar_uuid = None
    prof_uuid = None
    validate_parameters(params)
    hmc_host = params['hmc_host']
    hmc_user = params['hmc_auth']['username']
    password = params['hmc_auth']['password']
    system_name = params['system_name']
    vm_name = params['vm_name']
    prof_name = params['prof_name']
    keylock = params['keylock']
    iIPLsource = params['iIPLsource']

    try:
        rest_conn = HmcRestClient(hmc_host, hmc_user, password)
    except Exception as error:
        logger.debug(repr(error))
        module.fail_json(msg="Logon to HMC failed")

    try:
        system_uuid, server_dom = rest_conn.getManagedSystem(system_name)
        if not system_uuid:
            module.fail_json(msg="Given system is not present")

        lpar_response = rest_conn.getLogicalPartitionsQuick(system_uuid)
        if lpar_response:
            lpar_quick_list = json.loads(rest_conn.getLogicalPartitionsQuick(system_uuid))

        if lpar_quick_list:
            for eachLpar in lpar_quick_list:
                if eachLpar['PartitionName'] == vm_name:
                    partition_dict = eachLpar
                    lpar_uuid = eachLpar['UUID']
                    break

        if not lpar_uuid:
            module.fail_json(msg="Given Logical Partition is not present on given system")

        if prof_name:
            doc = rest_conn.getPartitionProfiles(lpar_uuid)
            profs = doc.xpath('//entry')
            for prof in profs:
                prof1 = etree.ElementTree(prof)
                pro_nam = prof1.xpath('//ProfileName/text()')[0]
                if prof_name == pro_nam:
                    prof_uuid = prof1.xpath('//id/text()')[0]
                    logger.debug(prof_uuid)
                    break

        logger.debug(prof_uuid)
        if prof_name and not prof_uuid:
            module.fail_json(msg="Given Logical Partition Profile is not present on given logical Partition")

        partition_state = partition_dict["PartitionState"]
        partition_type = partition_dict["PartitionType"]

        if partition_state == 'not activated':
            warn_msg = 'unsupported parameter iIPLsource passed to a partition type: '
            if partition_type != 'OS400' and iIPLsource:
                module.warn(warn_msg + partition_type)
            rest_conn.poweronPartition(lpar_uuid, prof_uuid, keylock, iIPLsource, partition_type)
            changed = True
        else:
            logger.debug("Given partition already in not activated state")
            return False, None

    except HmcError as hmcerr:
        err_msg = parse_error_response(hmcerr)
        if partition_type == 'OS400':
            resp_dict = json.loads(rest_conn.getLogicalPartitionQuick(lpar_uuid))
            ibmi_partition_state = resp_dict["PartitionState"]
            if ibmi_partition_state == 'error':
                module.warn(err_msg)
                changed = True
            else:
                logger.debug("Line number: %d exception: %s", sys.exc_info()[2].tb_lineno, repr(hmcerr))
                module.fail_json(msg=err_msg)
        else:
            logger.debug("Line number: %d exception: %s", sys.exc_info()[2].tb_lineno, repr(hmcerr))
            module.fail_json(msg=err_msg)

    except Exception as error:
        error_msg = parse_error_response(error)
        logger.debug("Line number: %d exception: %s", sys.exc_info()[2].tb_lineno, repr(error))
        module.fail_json(msg=error_msg)
    finally:
        try:
            rest_conn.logoff()
        except Exception as logoff_error:
            error_msg = parse_error_response(logoff_error)
            module.warn(error_msg)

    return changed, None


def perform_task(module):
    params = module.params
    actions = {
        "present": create_partition,
        "absent": remove_partition,
        "shutdown": poweroff_partition,
        "poweron": poweron_partition
    }

    oper = 'state'
    if params['state'] is None:
        oper = 'action'

    try:
        return actions[params[oper]](module, params)
    except (ParameterError, HmcError, Error) as error:
        return False, repr(error)


def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        hmc_host=dict(type='str', required=True),
        hmc_auth=dict(type='dict',
                      required=True,
                      no_log=True,
                      options=dict(
                          username=dict(required=True, type='str'),
                          password=dict(required=True, type='str'),
                      )
                      ),
        system_name=dict(type='str', required=True),
        vm_name=dict(type='str', required=True),
        proc=dict(type='int'),
        mem=dict(type='int'),
        os_type=dict(type='str', choices=['aix', 'linux', 'aix_linux', 'ibmi']),
        prof_name=dict(type='str'),
        keylock=dict(type='str', choices=['manual', 'norm']),
        iIPLsource=dict(type='str', choices=['a', 'b', 'c', 'd']),
        state=dict(type='str',
                   choices=['present', 'absent']),
        action=dict(type='str',
                    choices=['shutdown', 'poweron'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[('state', 'action')],
        required_one_of=[('state', 'action')],
        required_if=[['state', 'absent', ['hmc_host', 'hmc_auth', 'system_name', 'vm_name']],
                     ['state', 'present', ['hmc_host', 'hmc_auth', 'system_name', 'vm_name', 'os_type']],
                     ['action', 'shutdown', ['hmc_host', 'hmc_auth', 'system_name', 'vm_name']],
                     ['action', 'poweron', ['hmc_host', 'hmc_auth', 'system_name', 'vm_name']]
                     ]


    )

    if module._verbosity >= 1:
        init_logger()

    changed, result = perform_task(module)

    if isinstance(result, str):
        module.fail_json(msg=result)

    if result:
        module.exit_json(changed=changed, partition_info=result)
    else:
        module.exit_json(changed=changed)


def main():
    run_module()


if __name__ == '__main__':
    main()
