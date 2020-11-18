import syslog

from gpiozero import CPUTemperature
from time import sleep, strftime, time

if __name__ == "__main__":
    cpu = CPUTemperature()

    while True:
        syslog.syslog('CPU Temp {0} \n'.format(str(cpu.temperature)))

        sleep(300)
