"""This program is a Web service that accepts a number n as input from client and returns the first n Fibonacci numbers(start from 0)."""

import sys
import eventlet


g_dbg = True
g_cachedFib = {}
g_cachedFibStr = []
g_cachedFibSize = 0
g_serverAddr = "127.0.0.1"
g_listenPort = 7777
g_concurrency = 1000
g_senderSleep = 0.05
g_termStr = '-1'


#description:   function to print the help info of this program.	
#progname:      the name of the program.
def usage(progname):
    print("""
    This program is a Web service that accepts a number n as input from client and returns the first n Fibonacci numbers(start from 0).
    And please use Python 3 to run this program.

    Usage:          %s [option] serverAddr listenPort cachedFibSize concurrency senderSleep
    -h:             print this help message and exit (also --help)
    serverAddr:     the IP address of this Web server, '127.0.0.1' or equivalents can also be used
    listenPort:     the port number that this Web server will listen on
    cachedFibSize:  the size of the Fibonacci sequence(start from 0) that will be cached, be careful when setting this value,
                    and it is better to check the available system resources on your computer firstly
    concurrency:    the number of the GreenThread within eventlet's GreenPool
    senderSleep:    the interval time for returning each element within the Fibonacci sequence to the clients
    
    Run it like this:
                python %s <serverAddr> <listenPort> <cachedFibSize> <concurrency> <senderSleep>
                For example:   python problem2.py 127.0.0.1 7777 100 1000 0.03
    For help info:
                python %s -h or python %s --help
                
    Note:       please check the eventlet related info for the above parameters at http://eventlet.net/
    """ % (progname, progname, progname, progname))


#description:   A Memoized Fibonacci Function
#n:             the first n numbers of the Fibonacci sequence(n>=1 and fib(1)==0) will be calculated
#               and then cached in the global buffer
def fib(n):
    #print("server fib: n = %s" % n)
    if n in g_cachedFib:
        return g_cachedFib[n]
    if n == 1:
        g_cachedFib[1] = 0
        return 0
    if n == 2:
        g_cachedFib[2] = 1
        return 1

    val = fib(n - 1) + fib(n - 2)
    g_cachedFib[n] = val
    return val


#description:   Function as a Generator for Fibonacci sequence
#n:             the first n numbers of the Fibonacci sequence(n>=1 and fib(1)==0) will be generated
def fib_genr(n):
    a,b,i = 0, 1, 1
    while i <= n:
        yield a
        a, b = b, a + b
        i += 1


#description:   Function to initialize the cached Fibonacci sequence before start this Web service
#cachedFibSize: the first 'cachedFibSize' numbers of the Fibonacci sequence(n>=1 and fib(1)==0) will be calculated
#               and then cached in the global buffer
def init_p2(cachedFibSize):
    g_cachedFib[0] = 0
    fib(cachedFibSize)
    for i in range(cachedFibSize + 1):
        g_cachedFibStr.append(str(g_cachedFib[i]))


#description:   Function based on eventlet that handle client's request for returning the first n Fibonacci numbers
#client:        please check the following URIs for detailed info:
#                            http://eventlet.net/doc/basic_usage.html#primary-api,
#                            http://eventlet.net/doc/design_patterns.html
#                            http://eventlet.net/doc/examples.html
def fib_handler(client):
    if g_dbg:
        print("server fib_handler: client connected")
    while True:
        try:
            #read the request number from client, and pass through every non-eof line
            fibNum = int(client.readline())
            if g_dbg:
                print("server fib_handler: request number is ", fibNum)
            #error info will be returned to clients if the requested number is <= 0
            if fibNum <= 0:
                client.write("The value for Fibonacci Sequence should greater than 0!")
                client.flush()
                continue
            #if the requested the Fibonacci sequence is cached, then the cached result will be returned directly
            if fibNum <= g_cachedFibSize:
                for i in range(1, fibNum + 1):
                    #client.write(str(g_cachedFib[i]))
                    #if g_dbg:
                    #    print("g_cachedFibStr[%d] = %s" % (i, g_cachedFibStr[i]))
                    client.write(g_cachedFibStr[i])
                    client.flush()
                    eventlet.sleep(g_senderSleep)
                #send the terminator
                client.write(g_termStr)
                client.flush()
            #if the requested the Fibonacci sequence is not cached, then the result will be returned via a generator
            else:
                i = 0
                f = fib_genr(fibNum)
                while i < fibNum:
                    client.write(str(f.__next__()))
                    client.flush()
                    eventlet.sleep(g_senderSleep)
                    i += 1
                #send the terminator
                client.write(g_termStr)
                client.flush()
        except:
            client.close()
            break
    if g_dbg:
        print("server fib_handler: client disconnected")


if __name__ == '__main__':
    #the number of the command line parameters should be 2 or 6 for this program
    lenArgv = len(sys.argv)
    if g_dbg:
        print("server main: length of argv = %s" % lenArgv)
    if lenArgv < 2 or lenArgv > 6:
        #wrong number of the program arguments, print help info
        usage(sys.argv[0])
    else:
        if lenArgv == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
            #print help info of this program
            usage(sys.argv[0])
        else:
            if (lenArgv == 6):
                #configure this Web server
                g_serverAddr = sys.argv[1]
                g_listenPort = int(sys.argv[2])
                g_cachedFibSize = int(sys.argv[3])
                g_concurrency = int(sys.argv[4])
                g_senderSleep = float(sys.argv[5])
                #the maximum depth of the Python interpreter stack need to be reset since we use recursion in fib()
                #https://docs.python.org/3/library/sys.html?highlight=setrecursionlimit#sys.setrecursionlimit
                sys.setrecursionlimit(g_cachedFibSize << 1)
                #initialize the cached Fibonacci sequence before starting this Web server
                init_p2(g_cachedFibSize)

                server = eventlet.listen((g_serverAddr, g_listenPort))
                pool = eventlet.GreenPool(g_concurrency)
                while True:
                    new_sock, addr = server.accept()
                    if g_dbg:
                       print("server main: client connected from  ", addr)
                    pool.spawn_n(fib_handler, new_sock.makefile('rw'))
            else:
                #wrong input arguments, print help info
                usage(sys.argv[0])
    sys.exit()