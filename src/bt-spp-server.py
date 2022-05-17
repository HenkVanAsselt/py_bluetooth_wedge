# -------------------------------------------------------------------------------
# Name:        bt-spp-server.py
# Purpose:     Bluetooth Serial Port Profile server.
#
# Original source: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py
# pyperclip: https://github.com/asweigart/pyperclip
# pyautogui:
# -------------------------------------------------------------------------------

# Default imports
import sys
import socket
import configparser

# 3rd party imports
import bluetooth        # type: ignore
import pyautogui        # type: ignore
import pyperclip        # type: ignore

# Local imports
from src import bluetooth_address
from lib.helper import debug


def handler(a,b=None):
    sys.exit(1)


def install_handler():
    if sys.platform == "win32":
        import win32api
        win32api.SetConsoleCtrlHandler(handler, True)


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def init_bt_server(method="pybluez") -> tuple:
    """ Initialize the Bluetooth SPP server.
    Wait for a client to connect, and return the server socket, client socket and RFCOMM port

    :param method: "pybluez" or "socket"
    :param advertise: if True, advertise the service
    :return: Tuple of server socket, client socket and port
    """

    print("Initializing BT SPP Server")
    debug("Initalizing Bluetooth Wedge")

    # CC:2F:71:60:1F:0C
    if sys.platform == "win32":
        host_mac_address = bluetooth_address.get_bt_mac()
    else:
        host_mac_address = "CC:2F:71:60:1F:0C"
    print(f"BT address of this PC is {host_mac_address}")

    buf_size = 1024

    print(f"{method=}")
    if method == "socket":
        port = 0  # Normal port for rfcomm?
        server_sock = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        print(f"{server_sock=}")
        server_sock.bind((host_mac_address, port))
        server_sock.listen(1)
        try:
            print("Listening for connection...")
            client_sock, address = server_sock.accept()
            print(f"Connected to {address}")
            return server_sock, client_sock, port

            # while True:
            #     data = client_sock.recv(buf_size)
            #     if data:
            #         print(data)
        except Exception as e:
            print(f"Something went wrong: {e}")
            client_sock.close()
            server_sock.close()
        return None, None, None

    elif method == "pybluez":

        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", bluetooth.PORT_ANY))
        server_sock.listen(1)
        port = server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        bluetooth.advertise_service(
            server_sock,
            "Bluetooth_Wedge_Service",
            service_id=uuid,
            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE],
            # protocols=[bluetooth.OBEX_UUID]
        )

        try:
            print("Waiting for connection on RFCOMM channel", port)
            client_sock, client_info = server_sock.accept()
            print("Accepted connection from", client_info)
            client_sock.settimeout(0.1)
            return server_sock, client_sock, port
            # while 1:
            #     data = client_sock.recv(buf_size)
            #     if not data:
            #         break
            #     else:
            #         print(data)
        except OSError:
            pass

        print("Closing sockets")
        client_sock.close()
        server_sock.close()
        return None, None, None

    else:
        print(f"ERROR: Unknown {method=}")
        return None, None, None


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def wait_for_connection(server_sock, port):
    """Wait for incoming SPP connection

    :return: Client socket
    """

    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)
    return client_sock


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def get_data(server_sock, client_sock) -> bytes:
    """Get data from client socket"""

    # try:
    #     while True:
    #         data = client_sock.recv(1024)
    #         if len(data) == 0:
    #             print("datalen = ")
    #             break  # This will stop this generator
    #         if b"exit" in data:
    #             break
    #         print("generator received [%s]" % data)
    #         yield data  # Return data for this generator
    # except IOError:
    #     print("IOError. timeout?")
    #     pass
    # print("disconnected. Stopping generator")
    # return

    try:
        data = client_sock.recv(1024)
        if len(data) == 0:
            return b""
        elif b"exit" in data:
            return b""
        else:
            return data
    except KeyboardInterrupt:
        stop_server(server_sock, client_sock)
        return b""
    except IOError:
        # print("IOError. timeout?")
        return b""

    return b""

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def stop_server(client_sock, server_sock):
    """Stop the BT SPP server

    :return: Nothing
    """

    client_sock.close()
    server_sock.close()
    print("server stopped")
    return


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def wedge_by_typewriter(data):
    """Send the given data through pyautogui typewriter

    20171029 Warning: This does not handle control characters (yet)

    :param data: data to send to application window in foreground.
    :return: Nothing
    """

    print('Sending "%s" through typewriter' % data)
    pyautogui.typewrite("Wedged: %s" % data)
    return


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def wedge_by_clipboard(data):
    """Send the given data through pyperclip and pyautogui

    :param data: data to send to application window via clipboard
    :return: Nothing
    """

    print('Copying "%s" to clipboard' % data)
    pyperclip.copy("Clipboard: %s" % data)  # Send data to clipboard
    # pyperclip.paste()
    # pyautogui.hotkey("ctrl", "v")  # Paste the clipboard
    return


# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
def main():
    """Main application

    Start Bluetooth SPP Server and then loop through
        * wait for connection
        * Grab data
        * Process data
    """

    # See https://pymotw.com/2/ConfigParser/

    parser = configparser.ConfigParser()
    parser.read("config.ini")

    use_typewriter = parser.getboolean("wedge_method", "typewriter")
    use_clipboard = parser.getboolean("wedge_method", "clipboard")

    barcode_prestrip = parser.getint("barcode", "pre-strip")
    barcode_poststrip = parser.getint("barcode", "post-strip")
    print("barcode_prestrip = %s" % barcode_prestrip)
    print("barcode_poststrip = %s" % barcode_poststrip)

    barcode_prefix = bytes(parser.get("barcode", "prefix"), "utf-8")
    barcode_suffix = bytes(parser.get("barcode", "suffix"), "utf-8")
    print("prefix=%s" % barcode_prefix)
    print("suffix=%s" % barcode_suffix)

    # regex = None
    # regex_pattern = parser.get('barcode', 'regex_pattern')
    # regex_replacement = parser.get('barcode', 'regex_replacement')
    # if regex_pattern:
    #    regex = re.compile(regex_pattern)

    server_sock, client_sock, port = init_bt_server(method="pybluez")

    while True:

        # Get data from Bluetooth RFCOMM SPP port
        s = get_data(server_sock, client_sock)
        if not s:
            continue
        print(f"data = {s}")
        if b"exit" in s.lower():
            break

        # Barcode processing
        if barcode_prestrip:
            s = s[barcode_prestrip:]
            # print(f"After pre-strip: {s=}")
        if barcode_poststrip:
            s = s[:-barcode_poststrip]
            # print(f"After post-strip: {s=}")
        if barcode_prefix:
            s = barcode_prefix + s
            # print(f"After prefix:{s=}")
        if barcode_suffix:
            s = s + barcode_suffix
            # print(f"After suffix: {s=}")

        # if regex_pattern and regex_replacement:
        #     print('regular expression result: %s' % re.sub(regex_pattern, regex_replacement, s)

        if use_typewriter:
            wedge_by_typewriter(s)
            # pyautogui.press("enter")
            # pyautogui.press("enter")

        if use_clipboard:
            wedge_by_clipboard(s)
            # pyautogui.press("enter")
            # pyautogui.press("enter")

    # noinspection PyUnreachableCode
    stop_server(client_sock, server_sock)


if __name__ == "__main__":
    main()
