"""This program is a reference client for demoing or testing the Web service provided by problem2.py."""

import sys
import socket

g_dbg = True
g_host = ''
g_port = -1
g_bufsize = 4096


#description:   function to print the help info of this program.
#progname:      the name of the program.
def usage(progname):
    print("""
    This program is a reference client for demoing or testing the Web service provided by problem2.py.
    And please use Python 3 to run this program.

    Usage:          %s [option] serverAddr listenPort cachedFibSize concurrency senderSleep
    -h:             print this help message and exit (also --help)
    serverAddr:     the IP address of target Web server, '127.0.0.1' or equivalents can also be used
    serverPort:     the port number of target Web server

    Run it like this:
                python %s <serverAddr> <serverPort>
                For example:   python problem2_client.py 127.0.0.1 7777
    For help info:
                python %s -h or python %s --help

    Note:       please check the Python socket programming at https://docs.python.org/3/library/socket.html
    """ % (progname, progname, progname, progname))

if __name__ == '__main__':
    #the number of the command line parameters should be 3 for this program
    if len(sys.argv) != 3:
        usage(sys.argv[0])
    else:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            #print help info of this program
            usage(sys.argv[0])
        else:
             #configure the target Web server that will be connected to
             g_host = sys.argv[1]
             g_port = int(sys.argv[2])
             try:
                 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                 sock.connect((g_host, g_port))
             except socket.error as err:
                 print("Fail to create a socket")
                 print("reason: %s" % str(err))
                 sys.exit()
             print("Socket created, and successfully connect to %s on port %s" % (g_host, g_port))

             try:
                 while True:
                     #send the user input number to server
                     num = input("Please enter the number for requesting Fibonacci sequence from server: ")
                     sock.sendall(('%s\n' % num).encode())
                     #get response from server
                     print("Response from server: ")
                     while True:
                          data = sock.recv(g_bufsize)
                          #if g_dbg:
                          #    print("client main: received data = %s" % data)
                          try:
                              dataint = int(data)
                          except ValueError as err:
                              #handle the error info like the user input number is <= 0
                              print("%s " % data.decode())
                              break
                          else:
                              #handle the terminator
                              if dataint < 0:
                                  break
                              print("%d " % dataint, end = '')
                     print("\n")
             finally:
                 sock.close()
    sys.exit()