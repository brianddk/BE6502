#!/home/erin/src/BE6502/piControl/depends/wiringpi/.venv/bin/python3
from wiringpi import wiringPiSetupGpio, pinMode, digitalWrite, digitalRead, wiringPiISR, pullUpDnControl, delay
from wiringpi import INPUT, OUTPUT, HIGH, LOW, INT_EDGE_RISING, INT_EDGE_BOTH, PUD_DOWN
from sys import exit
from time import time

REQ  = 10
ACK  = 9
DATA = 11


ack = LOW
bInit = False
with open("send.bin", "rb") as f:
    sdata = f.read()
bitnum = 0
start = time()
bits = len(sdata) * 8

inv = lambda x: int(not bool(x))

def getbit(bnum):
    global sdata
    index = bnum // 8
    bit = bnum % 8
    byte = sdata[index]
    return (byte >> bit) & 0x01

def send():
    global bInit
    global bitnum
    global bits
    global start
    global ack
    # delay(1000)
    if not bInit:
        wiringPiISR(REQ, INT_EDGE_BOTH, send)
        bInit = True
        start = time()
    if bitnum < bits:        
        bit = getbit(bitnum)
        bitnum += 1
        # print(f"Writing bit number {bitnum}: {bit}")
        digitalWrite(DATA, bit)
        ack = inv(ack)
        digitalWrite(ACK, ack)
        # print(bit)
    else:
        elapsed = time() - start
        print(f"Data Done in {bits / elapsed} bps, exiting!")
        exit()        

if __name__ == "__main__":
    wiringPiSetupGpio()

    # Slave REQ
    pinMode(REQ, INPUT)
    pullUpDnControl(REQ, PUD_DOWN)

    # Slave ACK
    pinMode(ACK, OUTPUT)
    digitalWrite(ACK, ack)

    # Slave DATA
    pinMode(DATA, OUTPUT)
    digitalWrite(DATA, LOW)

    # Slave callback
    wiringPiISR(REQ, INT_EDGE_RISING, send)    
    
    try:
        while True:
            delay(1000)
            # send()
    except KeyboardInterrupt:
        print("\nExiting")
