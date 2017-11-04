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
#-------------------------------------------------------------------------------

from bluetooth import *
import sys

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

    print "Start reading data from connected BT device"

    try:
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            print("received [%s]" % data)
            assert isinstance(data, object)
            yield data
    except IOError:
        pass
    print("disconnected")
    return


def stop_server(client_sock, server_sock):
    """Stop the BT SPP server

    :return: Nothing
    """

    client_sock.close()
    server_sock.close()
    print "server stopped"
    return


def main():

    server_sock, port = init_bt_server()
    client_sock = wait_for_connection(server_sock, port)
    while True:
        s = get_data(client_sock)

    stop_server(client_sock, server_sock)


if __name__ == '__main__':
    main()
