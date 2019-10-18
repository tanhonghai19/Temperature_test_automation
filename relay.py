import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

Relays = [5, 6, 13, 19, 26, 16, 20, 21]

class Relay_module:
    def __init__(self):
        GPIO.setup(Relays, GPIO.OUT)

    def  reset(self):
        GPIO.output(Relays, GPIO.LOW)

    def RelaySelect(self, relay_num):
        GPIO.output(Relays[relay_num], GPIO.HIGH)

    def RelayDeSelect(self, relay_num):
        GPIO.output(Relays[relay_num], GPIO.LOW)


if __name__ == "__main__":
    REL= Relay_module()
    while True:
        for i in range (8):
            REL.RelaySelect(i)
            print(i)
            sleep(2)
            REL.RelayDeSelect(i)
            sleep(1)