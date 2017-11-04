#-------------------------------------------------------------------------------
# Name:        rfcomm-server-sdp.py
# Purpose:
#
# Author:      HenkA
#
# Created:     28/10/2017
# Copyright:   (c) HenkA 2017
# Licence:     <your licence>
#
# Original source: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py
# pyperclip: https://github.com/asweigart/pyperclip
# pyautogui:
#-------------------------------------------------------------------------------

# Global imports
import sys
import re
from ConfigParser import SafeConfigParser

# 3rd party imports
from bluetooth import *
import pyautogui
import pyperclip

def init_bt_server():
    """ Intialize the Blutooth SPP server

    :return: server socket and port
    """

    print "Initializing BT SPP Server"

    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    advertise_service(server_sock, "SampleServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE],
    #                 protocols=[OBEX_UUID]
                      )
    return server_sock, port


def wait_for_connection(server_sock, port):
    """Wait for incoming SPP connection

    :return: Client socket
    """

    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)
    return client_sock

def get_data(client_sock):
    """Get data from client socket
    """

    print "Start BT data generator"

    try:
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0:
                print 'datalen = 0'
                break   # This will stop this generator
            print("generator received [%s]" % data)
            yield data  # Return data for this generator
    except IOError:
        print 'IOError'
        pass
    print("disconnected. Stopping generator")
    return


def stop_server(client_sock, server_sock):
    """Stop the BT SPP server

    :return: Nothing
    """

    client_sock.close()
    server_sock.close()
    print "server stopped"
    return

def wedge_by_typewriter(data):
    """Send the given data through pyautogui typewriter

    20171029 Warning: This does not handle control characters (yet)

    :param data: data to send to application window in foregroudn
    :return: Nothing
    """

    print 'Sending "%s" through typewriter' % data
    pyautogui.typewrite('Wedged: %s' % data)
    return


def wedge_by_clipboard(data):
    """Send the given data through pyperclip and pyautogui

    :param data: data to send to application window via clipboard
    :return: Nothing
    """

    print 'Copying "%s" to clipboard' % data
    pyperclip.copy('Clipboard: %s' % data)        # Send data to clipboard
    # pyperclip.paste()
    pyautogui.hotkey('ctrl', 'v')  # Paste the clipboard
    return


def main():
    """Main application

    Start Bluetooth SPP Server and then loop through
        * wait for connection
        * Grab data
        * Process data
    """

    # See https://pymotw.com/2/ConfigParser/

    parser = SafeConfigParser()
    parser.read('config.ini')

    use_typewriter = parser.getboolean('wedge_method', 'typewriter')
    use_clipboard = parser.getboolean('wedge_method', 'clipboard')

    barcode_prestrip = parser.getint('barcode', 'pre-strip')
    barcode_poststrip = parser.getint('barcode', 'post-strip')
    print 'barcode_prestrip = %s' % barcode_prestrip
    print 'barcode_poststrip = %s' % barcode_poststrip

    barcode_prefix = parser.get('barcode', 'prefix')
    barcode_suffix = parser.get('barcode', 'suffix')
    print 'prefix=%s' % barcode_prefix
    print 'suffix=%s' % barcode_suffix

    regex = None
    regex_pattern = parser.get('barcode', 'regex_pattern')
    regex_replacement = parser.get('barcode', 'regex_replacement')

    #if regular_expression:
    #    regex = re.compile(regular_expression)


    server_sock, port = init_bt_server()

    while True:
        client_sock = wait_for_connection(server_sock, port)
        for s in get_data(client_sock):
            print 'data = %s' % repr(s)
            if barcode_prestrip:
                s = s[barcode_prestrip:]
                print 'After pre-strip: data = %s' % s
            if barcode_poststrip:
                s = s[:-barcode_poststrip]
                print 'After post-strip: data = %s' % s
            if barcode_prefix:
                s = barcode_prefix + s
                print 'After prefix: data = %s' % s
            if barcode_suffix:
                s = s + barcode_suffix
                print 'After suffix: data = %s' % s
            if regex_pattern and regex_replacement:
                print 'regular expression result: %s' % re.sub(regex_pattern, regex_replacement, s)

            if use_typewriter:
                wedge_by_typewriter(s)
                pyautogui.press('enter')
                pyautogui.press('enter')

            if use_clipboard:
                wedge_by_clipboard(s)
                pyautogui.press('enter')
                pyautogui.press('enter')

    # noinspection PyUnreachableCode
    stop_server(client_sock, server_sock)


if __name__ == '__main__':
    main()






