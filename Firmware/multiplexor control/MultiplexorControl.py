import numpy as np
import time
import threading
import RPi.GPIO
from smbus2 import SMBus  
from pathdict import pathdata


class Multi_board:
    def __init__(self):
        self.registers = {  
            'IODIR' : 0x00,
            'IPOL' : 0x01,
            'GPINTEN' : 0x02,
            'DEFVAL' : 0x03,
            'INTCON' : 0x04,
            'IOCON' : 0x05,
            'GPPU' : 0x06,
            'INTF' : 0x07,
            'INTCAP' : 0x08,
            'GPIO' : 0x09,
            'OLAT' : 0x0A 
        }
        self.slv_addresses = {  #default, but may need to be overwritten for diffrent boards as it is hardware addressed.
            0 : 0x21,
            1 : 0x22,
            2 : 0x23,
            3 : 0x24 
        }
        self.bus = SMBus(1)

    def reg_data(self, pth_s):
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

    def compile_reg_data(self, pth_s):
    # This function feeds the data to the reg_data function and then converts it into hex data. 

        cmd_hex = []                    # stores (on_regs, off_regs) in hex form
        for matrix in self.reg_data(pth_s):
            reg_hex = []

            for row in matrix: 
                b = ''                  # technically this does not need to be a string, but i like to see the leading zeros in a 8-bit binary string. 00001000.
                for m in reversed(row): # this reverses the marix binary string as a 0000 0001 in binary is represented as 1000 0000 in the matrix
                    b += str(m)
                c = int(b, 2)
                reg_hex.append(c)       # outputs hex register values in list, (reg1,reg2,reg3,reg4)
            cmd_hex.append(reg_hex)

        return cmd_hex
        
    def wrt_reg_data(self, pth_s,v):          
    # sends the cmd_hex data to the i2c bus and ultimately the slaves, v selects the onstate(1) or offstate(0)

        a = self.compile_reg_data(pth_s)
        c = 0                           # from the cmd_hex nested list.
        for n in a[v]:
            self.bus.write_byte_data(self.slv_addresses[c], self.registers['GPIO'], n)       # uncomment when on pi
            c += 1


    def configure_slaves(self):             
    # sets the slave configurations register on each device.
        print('configuring')
        for i in range(len(self.slv_addresses)):
            self.bus.write_byte_data(self.slv_addresses[i], self.registers['IOCON'], 0x3a)       # uncomment when on pi
            self.bus.write_byte_data(self.slv_addresses[i], self.registers['IODIR'], 0x00)


def main():
    MB = Multi_board()
    MB.configure_slaves()
    time.sleep(1)
    MB.wrt_reg_data(((1,1),(2,9),(3,5),(4,13)),0)
    time.sleep(3)
    MB.wrt_reg_data(((1,1),(2,9),(3,5),(4,13)),1)
    time.sleep(2)
    MB.wrt_reg_data(((1,1),(2,9),(3,5),(4,13)),0)

if __name__ == '__main__':
    main()



