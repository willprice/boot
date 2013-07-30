from multiprocessing import Process, Pipe
from subprocess import call, Popen, PIPE, STDOUT
import time, os, signal, sys

def f(conn):
    print 'go'

    # make a system process
    #cmd = 'find /lib -name f*'
    cmd = 'find / -name f*'
    p = Popen(cmd.split(), shell=False, stdout=PIPE, stderr=STDOUT)
    print 'Process created, id:', p.pid

    # send process id
    conn.send(p.pid)

    cmd = 'find /lib -name f*'
    p = Popen(cmd.split(), shell=False, stdout=PIPE, stderr=STDOUT)
    print 'Process created, id:', p.pid

    # send process id
    conn.send(p.pid)

    cmd = 'find /lib -name f*'
    p = Popen(cmd.split(), shell=False, stdout=PIPE, stderr=STDOUT)
    print 'Process created, id:', p.pid

    # send process id
    conn.send(p.pid)

    # print results
    for line in p.stdout.readlines():
        pass
        print line

if __name__ == '__main__':

    reply = []
    comm_i, comm_o = Pipe()
    _p = Process(target=f, args=(comm_o,))
    _p.start()

    time.sleep(10)

    # collect all processes ids
    while comm_i.poll():
        reply.append(comm_i.recv())
    print 'running processes:', reply

    # kill all running processes
    for x in reply:
        try:
            os.kill(x, signal.SIGKILL)
            print "I've killed process id:", x
        except:
            pass

    _p.terminate()
    _p.join()
    print 'bye'
