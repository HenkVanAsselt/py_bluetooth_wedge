"""Windows bluetooth low level functions by means of WMI

See https://github.com/tjguk/wmi/blob/master/docs/tutorial.rst
See https://github.com/tjguk/wmi/blob/master/docs/cookbook.rst
"""

import wmi  # type: ignore

c = wmi.WMI()

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def get_bt_mac() -> str:
    """Get the BT mac address of the first bluetooth adapter on this PC
    :returns: mac address as a string
    """
    for interface in c.Win32_NetworkAdapterConfiguration():
        if "Bluetooth" in interface.Description:
            print(interface)
            # print(interface.Description, interface.MACAddress)
            return interface.MACAddress
    return ""


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    mac = get_bt_mac()
    print(f"{mac=}")
