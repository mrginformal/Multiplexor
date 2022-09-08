from Mcontrol import send_state_cmd
import time


def main():
    send_state_cmd(((1,1),), 10)
    time.sleep(6)
    #send_state_cmd(((2,11)),5)

if __name__ == '__main__':
    main()