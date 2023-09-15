#!/home/erin/src/BE6502/piControl/depends/wiringpi/.venv/bin/python3
from wiringpi import wiringPiSetupGpio, pinMode, digitalWrite, digitalRead, wiringPiISR, pullUpDnControl, delay
from wiringpi import INPUT, OUTPUT, HIGH, LOW, INT_EDGE_RISING, INT_EDGE_BOTH, PUD_DOWN
from sys import exit
from time import time

BO  = 17 # doorBell Out; REQ
BI  = 27 # doorBell In;  ACK
RX  = 22 # Receive In;   DATA

            # with open("recv.bin", "rb") as f:
                # sdata = f.read()
bo = LOW
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
    global bo
    global rch
    global rdata
    # delay(1000)
    if not bInit:
        wiringPiISR(BI, INT_EDGE_BOTH, recv)
        bInit = True
        
    dbit = digitalRead(RX)
    # print(f"Read bit {bitnum}: {dbit}")
    byte = bitnum // 8
    bit  = bitnum % 8
    rch = setbit(dbit, rch, bit)

    if bit==7 and byte==len(rdata):
        rdata += rch.to_bytes()
        rch    = 0x00
        # print(f"RDATA: {rdata}")
        
    bitnum += 1
    bo = inv(bo)
    digitalWrite(BO, bo)
    # Infinate recussion, you don't finish this line before interrupted again.

if __name__ == "__main__":
    wiringPiSetupGpio()

    # Master BO
    pinMode(BO, OUTPUT)
    digitalWrite(BO, bo)

    # Master BI
    pinMode(BI, INPUT)
    pullUpDnControl(BI, PUD_DOWN)

    # Master RX
    pinMode(RX, INPUT)
    pullUpDnControl(RX, PUD_DOWN)

    # Master callback
    wiringPiISR(BI, INT_EDGE_RISING, recv)    
    
    # Start things off
    bo = inv(bo)
    digitalWrite(BO, bo)
    
    try:
        while True:
            delay(1000)
            # recv()
    except KeyboardInterrupt:
        print("\nExiting")
