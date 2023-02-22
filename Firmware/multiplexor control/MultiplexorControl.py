import numpy as np
import time
import threading
#import RPi.GPIO                    #uncomment on pi
from smbus2 import SMBus  
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

BUS_1 = SMBus(1)                   # uncomment on pi --- Ensure connected to appropriate bus

slv_addresses = {                  # enter when part recieved 
# ***CURRENT VALUES FOR UNIT 1***
    0 : 0x21,
    1 : 0x22,
    2 : 0x23,
    3 : 0x24
}

def reg_data(pth_s):
# This fuction builds the register data in the form of a matrix, it builds both a on and off state (same connects with exception of the first colum of relays)
# Each row is the register of a diffrent slave, slave one being row one and so on. There is also a is active matrix which tracks if the relay have a signal
# being sent through it, if two paths try to set a rela y to active(writing a 1 to the matrix) that indicates the paths would share a bus, cuasing a short circuit.
# Note: already active pertains to one already used within the same command. not previous commands or states.

    reg_packet = np.zeros([4,8], dtype = int)
    active_pth = np.zeros([4,8], dtype = int)

    for path in pth_s:
        for relay in pathdata[path]:
            reg_packet[relay[0] - 1][relay[1]] = relay[2]       # writes the 1's and zero's based on data from pathdict file

            if active_pth[relay[0] - 1][relay[1]] == 1:         # checks if the relay is already used by a path, if so raises value error, otherwise sets it to in use state.
                raise ValueError('Short Circuit detected from path command {}, select diffrent paths and refer to connection diagram to ensure paths do not cross'.format(str(pth_s)))
            else:
                active_pth[relay[0] - 1][relay[1]] = 1

    on_regs = reg_packet
    off_regs = np.matrix.copy(on_regs)                            # makes off reg by forcing all double pole single throw relays to off but maintains other connections
    off_regs[0][0:4] = 0

    return (off_regs, on_regs)    

def compile_reg_data(pth_s):
# This function feeds the data to the reg_data function and then converts it into hex data. 

    cmd_hex = []                    # stores (on_regs, off_regs) in hex form
    for matrix in reg_data(pth_s):
        reg_hex = []

        for row in matrix: 
            b = ''                  # technically this does not need to be a string, but i like to see the leading zeros in a 8-bit binary string. 00001000.
            for m in reversed(row): # this reverses the marix binary string as a 0000 0001 in binary is represented as 1000 0000 in the matrix
                b += str(m)
            c = int(b, 2)
            reg_hex.append(c)       # outputs hex register values in list, (reg1,reg2,reg3,reg4)
        cmd_hex.append(reg_hex)

    return cmd_hex

def send_state_cmd(pth_s,duration):
 # This simply multithreads out the timers and then calls to actually write the data when nessisary
    wrt_reg_data(pth_s,0)
    time.sleep(.25)
    wrt_reg_data(pth_s, 1)
    time.sleep(duration)
    wrt_reg_data(pth_s,0)
    time.sleep(.25)

    
def wrt_reg_data(pth_s,v):          
# sends the cmd_hex data to the i2c bus and ultimately the slaves, v selects the onstate(1) or offstate(0)

    a = compile_reg_data(pth_s)
    c = 0                           # from the cmd_hex nested list.
    for n in a[v]:
        BUS_1.write_byte_data(slv_addresses[c], GPIO, n)       # uncomment when on pi
        c += 1


def cycle_all(duration):           
# this function will cycle through all of the path options, thus every input gets tested at every output for the duraiton

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
            n += 1
                
     
def configure_slaves():             
# sets the slave configurations register on each device.
    print('configuring')
    for i in range(len(slv_addresses)):
        BUS_1.write_byte_data(slv_addresses[i], IOCON, 0x3a)       # uncomment when on pi
        BUS_1.write_byte_data(slv_addresses[i], IODIR, 0x00)


def main():
    configure_slaves()
    time.sleep(1)
    print('executing')
    try:
        
        send_state_cmd(((1,1),(2,9),(3,5),(4,13)), 10)
        send_state_cmd(((1,16),(2,5),(3,9),(4,1)), 5)
        '''
        t1 = threading.Thread(target=cycle_all,args=[2])
        t1.start()
        '''
    except ValueError as err:
        print(err)


if __name__ == '__main__':
    main()



