#!/home/erin/src/BE6502/piControl/depends/wiringpi/.venv/bin/python3
from wiringpi import wiringPiSetupGpio, pinMode, digitalWrite, digitalRead, wiringPiISR, pullUpDnControl, delay
from wiringpi import INPUT, OUTPUT, HIGH, LOW, INT_EDGE_RISING, INT_EDGE_BOTH, PUD_DOWN
from sys import exit
from time import time

REQ  = 17
ACK  = 27
DATA = 22

            # with open("recv.bin", "rb") as f:
                # sdata = f.read()
req = LOW
bInit = False
bitnum = 0
rdata = b''
rch   = 0x00

inv = lambda x: int(not bool(x))

def setbit(dbit, ch, bit):
    return (dbit << bit) | ch

def recv():
    global bInit
    global bitnum
    global req
    global rch
    global rdata
    # delay(1000)
    if not bInit:
        wiringPiISR(ACK, INT_EDGE_BOTH, recv)
        bInit = True
        
    dbit = digitalRead(DATA)
    # print(f"Read bit {bitnum}: {dbit}")
    byte = bitnum // 8
    bit  = bitnum % 8
    rch = setbit(dbit, rch, bit)

    if bit==7 and byte==len(rdata):
        rdata += rch.to_bytes()
        rch    = 0x00
        # print(f"RDATA: {rdata}")
        
    bitnum += 1
    req = inv(req)
    digitalWrite(REQ, req)
    # Infinate recussion, you don't finish this line before interrupted again.

if __name__ == "__main__":
    wiringPiSetupGpio()

    # Master REQ
    pinMode(REQ, OUTPUT)
    digitalWrite(REQ, req)

    # Master ACK
    pinMode(ACK, INPUT)
    pullUpDnControl(ACK, PUD_DOWN)

    # Master DATA
    pinMode(DATA, INPUT)
    pullUpDnControl(DATA, PUD_DOWN)

    # Master callback
    wiringPiISR(ACK, INT_EDGE_RISING, recv)    
    
    # Start things off
    req = inv(req)
    digitalWrite(REQ, req)
    
    try:
        while True:
            delay(1000)
            # recv()
    except KeyboardInterrupt:
        print("\nExiting")
