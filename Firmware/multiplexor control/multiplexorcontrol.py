import numpy as np
import time
import threading
#import RPi.GPIO                    #uncomment on pi
#from smbus import SMBus  
from pathdict import pathdata

#23008 Registers

IODIR = 0x00
IPOL = 0x01
GPINTEN = 0x02
DEFVAL = 0x03
INTCON = 0x04
IOCON = 0x05
GPPU = 0x06
INTF = 0x07
INTCAP = 0x08
GPIO = 0x09
OLAT = 0x0A

#Bus and slave addresses

#BUS_1 = SMBus(1)                   # uncomment on pi

slv_addresses = {                   # enter when part recieved
    0 : 'hexaddress1',
    1 : 'hexaddress2',
    2 : 'hexaddress3',
    3 : 'hexaddress4'
}

def build_reg_data(pth):            # this creates the matrix and puts the values in the correct locations defined by pathdict file
    reg_packet = np.zeros([4,8], dtype = int)

    for n in pathdata[pth]:
            reg_packet[n[0] - 1][n[1]] = n[2]

    return reg_packet

def combine_reg_data(pth_s):        # This combines the 4 paths into one matrix, then converts to binary and then hex
    r = np.zeros([4,8], dtype = int)
    for x in pth_s:
        r += build_reg_data(x)      # matrix sum should happen here (this is the 'on state' matrix)
    j = np.matrix.copy(r)           # this simply copies the 'on state' matrix with the 4 input relays being forced to off.
    j[0][0:4] = 0.
    short_circuit_check(r,pth_s)
    return (r,j)

def short_circuit_check(pth_mtrx,pth_s):         # checks the combine_reg_data matrix to see if the set of paths intersect aka share a bus. typically not good.
    if pth_mtrx[0][6] == pth_mtrx[1][0] or pth_mtrx[0][4] == pth_mtrx[0][5] or pth_mtrx[1][1] == pth_mtrx[1][2] or pth_mtrx[1][3] == pth_mtrx[1][4]: # feels dumb to use this many "if or" statements
        #print(pth_mtrx[0][6], pth_mtrx[1][0], pth_mtrx[0][4], pth_mtrx[1][2], pth_mtrx[1][1], pth_mtrx[1][2], pth_mtrx[1][3], pth_mtrx[1][4])      # see what matrix data triggers error
        raise ValueError('Short Circuit detected from path command {}, select diffrent paths and refer to connection diagram to ensure paths do not cross'.format(str(pth_s)))

def compile_reg_data(pth_s):
    cmd_hex = []                    # will store both off state and on state register data(onstate reg_data, offstate reg_data)
    for p in combine_reg_data(pth_s):
        reg_hex = []

        for n in p: 
            b = ''                  # technically this does not need to be a string, but i like to see the leading zeros in a 8-bit binary string. 00001000.
            for m in reversed(n):   # this reverses the marix binary string as a 0000 0001 in binary is represented as 1000 0000 in the matrix
                b += str(m)
            c = hex(int(b, 2))
            reg_hex.append(c)       # outputs hex register values in list, (reg1,reg2,reg3,reg4)
        cmd_hex.append(reg_hex)

    return cmd_hex

def send_state_cmd(pth_s,duration): # This simply multithreads out the timers and then calls to actually write the data when nessisary
    t1 = threading.Timer(.5, wrt_reg_data,[pth_s,0])                
    t2 = threading.Timer(float(duration) + .5, wrt_reg_data,[pth_s,1]) 
    wrt_reg_data(pth_s,1)
    t1.start()
    t2.start()

def wrt_reg_data(pth_s,v):          # sends the cmd_hex data to the i2c bus and ultimately the slaves, v selects the onstate or offstate
    a = compile_reg_data(pth_s)
    c = 0                           # from the cmd_hex nested list.
    for n in a[v]:
        #BUS_1.write_byte_data(slv_addresses[c],IODIR,n)       # uncomment when on pi
        print(slv_addresses[c],n)
        c += 1


def cycle_all(duration):            # this function will cycle through all of the path options, thus every input gets tested at every output for the duraiton
    a = [
        ((1,1),(2,9),(3,5),(4,13)), # do to the limits of the board and since certain paths cannot be connected at the same time as others.
        ((1,5),(2,13),(3,1),(4,9)), # there are 4 distinct path sets encoded in this data, we cycle 4 times, then switch path sets in order to avoid problems
        ((1,9),(2,1),(3,13),(4,5)),
        ((1,13),(2,5),(3,9),(4,1))
        ]
    for b in a:                     # this performs the 4 cycles before the switch to the next path set.
        n = 0
        while n < 4:
            x = []
            for c in b:
                x.append((c[0],c[1]+n))
            send_state_cmd(x,duration)                            
            time.sleep(duration + 1)
            n += 1
                

def configure_slaves():             # sets the slave configurations register on each device.
    for i in range(len(slv_addresses)):
        #BUS_1.write_byte_data(slv_addresses[i], IOCON, 0x0A)       # uncomment when on pi
        print(slv_addresses[i], 0x0A)

def main():
    # send_state_cmd(((1,1),(3,5),(2,9),(4,13)), 10)
    # configure_slaves()
    t1 = threading.Thread(target=cycle_all,args=[3])
    t1.start()

if __name__ == '__main__':
    main()



