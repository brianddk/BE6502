#!/usr/bin/env micropython
# Video #01 from BE6502: https://youtu.be/playlist?list=PLowKtXNTBypFbtuVMUVXNR0z1mu7dp7eH
# Serves as the Arduino and resistors https://youtu.be/LnzuMJLZRdU?t=1195

# Max speed                    = 1.521563 KHz stripped at https://wokwi.com/projects/new/micropython-pi-pico
# Max busy toggle              = 82.34977 KHz
# Max blocking FIFO PIO toggle = 66.70113 KHz

from sys import implementation
assert hasattr(implementation, '_machine') and 'Pi Pico' in implementation._machine, "Must be run on Raspberry Pi Pico"

from rp2 import bootsel_button
from machine import Pin, unique_id
from time import sleep_us, ticks_us, ticks_diff, ticks_add

class BootSelButton(Exception):
    pass

address_pins = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in [0,1,2,3,4,5,6,7,8,9,10,11,15,14,13,12]]
data_pins = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in [26,22,21,20,19,18,17,16]]
rwb = Pin(27, Pin.IN, Pin.PULL_DOWN)
phi = Pin(28, Pin.OUT, Pin.PULL_UP)

FREQ = 5 # Hz, max = 1239
USDELAY = int(1_000_000 / FREQ / 2)            # 1 cycle = 2 waits
DATA = 0xEA                                    # Default for this video
LED = Pin(25, Pin.OUT)
SN = unique_id()
REAL_HW = bool(int.from_bytes(SN, 'big'))      # WokWi emulators have 0x0000 as SN

def get_data(data_pins):
    data = 0
    for i, pin in enumerate(data_pins):
        if pin.value():
            data |= (1 << i)
    return data

def provide_data(data_pins, data):
    for i, pin in enumerate(data_pins):
        if data & (1 << i):
            pin.value(1)
        else:
            pin.value(0)

def set_data_in(data_pins):
    for pin in data_pins:
        pin.init(mode=Pin.IN)

def set_data_out(data_pins):
    for pin in data_pins:
        pin.init(mode=Pin.OUT)

def pull_pins(pins, pulls):
    for i, pin in enumerate(pins):
        if pulls & 1 << i:
            pin.init(Pin.IN, Pin.PULL_UP)
        else:
            pin.init(Pin.IN, Pin.PULL_DOWN)

def main():
    # Set Pulls to give floating pins defaults
    pull_pins(address_pins, 0xEAEA)
    pull_pins(data_pins, 0xEA)
    pull_pins([rwb], 1)
    # Stall start
    print("Momentary press BOOTSEL to start, then hold button to end")
    while True:
        if not bootsel_button(): continue
        sleep_us(500 * 1000)              # 500ms debounce
        break

    ro = True
    end = ticks_add(ticks_us(), USDELAY)  # end future sleep after DELAY microseconds
    try:
        # CYCLES = 1000                       # stub code for timing tests
        # tstart = ticks_us()                 # stub code for timing tests
        # for i in range(0,CYCLES):
        while True:
            data = DATA
            phi.value(0)
            LED.value(0)
            sleep_us(ticks_diff(end, ticks_us()))
            end = ticks_add(ticks_us(), USDELAY)
            data_req = rwb.value()
            if data_req:
                set_data_out(data_pins)
                provide_data(data_pins, data)
            else:
                set_data_in(data_pins)
            address = get_data(address_pins)
            phi.value(1)
            LED.value(1)
            sleep_us(ticks_diff(end, ticks_us()))
            end = ticks_add(ticks_us(), USDELAY)
            if not data_req:
                data = get_data(data_pins)
            print("{} Address: 0x{:04X} Data: 0x{:02X}".format("r" if data_req else "W", address, data))
            if REAL_HW and bootsel_button(): raise BootSelButton

        # tend = ticks_us()
        # ms = ticks_diff(tend,tstart) / 1000
        # KHz = CYCLES/ms
        # print("KHz", KHz, "ms", ms)

    except KeyboardInterrupt:
        print("Caught Stop Req")
    except BootSelButton:
        print("Caught Stop Button")
    except Exception as e:
        print(f"Opps... Unexpected error caught: {e}")
    LED.value(0)


if __name__ == "__main__":
    print("Hello World")
    main()