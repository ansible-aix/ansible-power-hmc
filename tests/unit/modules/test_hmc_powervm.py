from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
import importlib

IMPORT_HMC_POWERVM = "ansible_collections.ibm.power_hmc.plugins.modules.powervm_lpar_instance"

from ansible_collections.ibm.power_hmc.plugins.module_utils.hmc_exceptions import ParameterError
from lxml import etree

hmc_auth = {'userid': 'hscroot', 'password': 'password_value'}
test_data = [
    # ALL Create partition testdata
    #system name is missing 
    ({'hmc_host': "0.0.0.0", 'hmc_auth': hmc_auth, 'system_name': None, 'vm_name': "vmname", 'proc': '4', 'mem':'2048', 'os_type':'aix_linux'},"ParameterError: mandatory parameter 'system_name' is missing"), 
    #vmname is missing
    ({'hmc_host': "0.0.0.0", 'hmc_auth': hmc_auth, 'system_name': "systemname", 'vm_name': None, 'proc': '4', 'mem':'2048', 'os_type':'aix_linux'},"ParameterError: mandatory parameter 'vm_name' is missing"),
    #proc is missing
    ({'hmc_host': "0.0.0.0", 'hmc_auth': hmc_auth, 'system_name': "systemname", 'vm_name': "vmname", 'proc': None, 'mem':'2048', 'os_type':'aix_linux'},"ParameterError: mandatory parameter 'proc' is missing"),
    # mem is missing
    ({'hmc_host': "0.0.0.0", 'hmc_auth': hmc_auth, 'system_name': "systemname", 'vm_name': "vmname", 'proc': '4', 'mem':None, 'os_type':'aix_linux'},"ParameterError: mandatory parameter 'mem' is missing"),
    #os type is missing
    ({'hmc_host': "0.0.0.0", 'hmc_auth': hmc_auth, 'system_name': "systemname", 'vm_name': "vmname", 'proc': '4', 'mem':'2048', 'os_type': None},"ParameterError: mandatory parameter 'os_type' is missing")
    ]

def common_mock_setup(mocker):
    hmc_powervm = importlib.import_module(IMPORT_HMC_POWERVM)
    mocker.patch.object(hmc_powervm, 'HmcCliConnection')
    return hmc_powervm

@pytest.mark.parametrize("powervm_test_input, expectedError", test_data)
def test_call_inside_powervm_hmc(mocker, powervm_test_input, expectedError):
    hmc_powervm = common_mock_setup(mocker)
    if 'ParameterError' in expectedError:
        with pytest.raises(ParameterError) as e:
            hmc_powervm.create_partition(hmc_powervm, powervm_test_input)
        assert expectedError == repr(e.value)
    else:
        hmc_powervm.create_partition(hmc_powervm, powervm_test_input)
