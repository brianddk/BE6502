#!/usr/bin/env micropython
# Video #01 from BE6502: https://youtu.be/playlist?list=PLowKtXNTBypFbtuVMUVXNR0z1mu7dp7eH
# Serves as the Arduino and resistors https://youtu.be/LnzuMJLZRdU?t=1195

# This PIO version of the Arduino debugger executes AFTER rising/falling edge.  May modify to run BEFORE falling/raising edge

# To learn PIO, good sections of study are:
# 1. RP2040 Datasheet Ch3 - https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=310
# 2. Pico Python Manual Sec3.9 - https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf#_pio_support
# 3. Pico C++ Manual Ch3 - https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-c-sdk.pdf#page=30
# 4. Micropython `rp2` module - https://docs.micropython.org/en/latest/library/rp2.html

from sys import implementation, exit
assert hasattr(implementation, '_machine') and 'Pico' in implementation._machine, "Must be run on Raspberry Pi Pico"

from machine import Pin, unique_id
from time import sleep_us, ticks_us, ticks_diff, ticks_add
from rp2 import asm_pio, StateMachine, PIO, bootsel_button

class BootSelButton(Exception):
    pass

# KHz 7.566465 ms 1189.459 stripped at https://wokwi.com/projects/new/micropython-pi-pico
# KHz 6.859191 ms 1312.108 without NULL sleep with bootsel check
# KHz 4.987238 ms 1804.606 with NULL sleep and bootsel check

FREQ = 5                                       # Hz, max ~ 5000, but much above 500 will overflow the print buffers
USDELAY = int(1_000_000 / FREQ / 2)            # 1 cycle = 2 waits
DATA = 0xEA                                    # Default for this video
LED = Pin(25, Pin.OUT)
SN = unique_id()
REAL_HW = bool(int.from_bytes(SN, 'big'))      # WokWi emulators have 0x0000 as SN

# 4 bit lookup table to do 4 bit reversals.
rev = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]

# Pin hookup array from LSB to MSB       # reversed / overlayed
AN0 = [Pin(i) for i in [ 0,  1,  2,  3]]          # 3210
AN1 = [Pin(i) for i in [ 4,  5,  6,  7]]          # 7654
AN2 = [Pin(i) for i in [ 8,  9, 10, 11]]          # BA98
AN3 = [Pin(i) for i in [12, 13, 14, 15]] # reverse  CDEF
DN1 = [Pin(i) for i in [16, 17, 18, 19]] # reverse  4567
DN0 = [Pin(i) for i in [19, 20, 21, 22]] # rev_ovly 1234
DB0 = [Pin(i) for i in [26            ]]          #    0
RWB = [Pin(i) for i in [27            ]]
PHI = [Pin(i) for i in [28            ]]

# State Machines
# 0 - A0-A3 (sm_an0)
# 1 - A4-A7 (sm_an1)
# 2 - A8-A11 (sm_an2)
# 3 - A12-A15 (sm_an3)
# 4 - D7-D4 (sm_dn1)
# 5 - D4-D1 (sm_dn0) (overlay)
# 6 - D0 (sm_db0)
# 7 - PHI, RWB (sm_phirwb)

# Pin connections
# {A0-A11} -> {GP0-GP11}
# {A15-A12} -X-> {GP12-GP15}  # MSB / LSB reversal
# {D7-D1} -X-> {GP16-GP22}    # MSB / LSB reversal
# {D0} -> {GP26}
# {RWB} -> {GP27}
# {PHI2} -> {GP28}

# Given a list of pins, set them as input with specific pull values
def pull_pins(pins, pulls):
    for i, pin in enumerate(pins):
        if pulls & 1 << i:
            pin.init(Pin.IN, Pin.PULL_UP)
        else:
            pin.init(Pin.IN, Pin.PULL_DOWN)

# Set Pulls to give floating pins defaults
pull_pins(AN0 + AN1 + AN2 + AN3[::-1], 0xEAEA)
pull_pins(DB0 + DN0[::-1][:-1] + DN1[::-1], 0xEA)
pull_pins(RWB, 1)

# Stall start
print("Momentary press BOOTSEL to start, then hold button to end")
while True:
    if not bootsel_button(): continue
    sleep_us(500 * 1000)              # 500ms debounce
    break

# 4 bit state machine to read address nibbles
@asm_pio(autopush = True)
def pio_an():
    PHI = 28                        # PHI pin constant
    NIBBLE = 4                      # NIBBLE = 4 bits
    OUTPUT = HIGH = 1               # OUTPUT on 1 and "HIGH" level on 1
    INPUT = LOW = 0                 # INPUT on 0 and "LOW" level on 0

    wrap_target()                   # __ - "TOP:"
    wait(HIGH, gpio, PHI)           # 01 - Wait for PHI high
    in_(pins, NIBBLE)               # 02 - Shift data from pins
    wait(LOW, gpio, PHI)            # 03 - Wait for PHI low
    wrap()                          # __ - JMP to top

# Create state machine for each address nibble to read.
sm_an0 = StateMachine(0, pio_an, in_base = AN0[0], in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(AN0))
sm_an1 = StateMachine(1, pio_an, in_base = AN1[0], in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(AN1))
sm_an2 = StateMachine(2, pio_an, in_base = AN2[0], in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(AN2))
sm_an3 = StateMachine(3, pio_an, in_base = AN3[0], in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(AN3)) # do reversal after read

# 4 bit state machine to R/W data pins based on RWB
@asm_pio(out_init=tuple([PIO.OUT_LOW] * len(DN1)), set_init=tuple([PIO.OUT_LOW] * len(DN1)), autopush = True, autopull = True)
def pio_dn():
    PHI = 28                        # PHI pin constant
    NIBBLE = 4                      # Long NIBBLE = 5 bits
    OUTPUT = HIGH = 1               # OUTPUT on 1 and "HIGH" level on 1
    INPUT = LOW = 0                 # INPUT on 0 and "LOW" level on 0

    wrap_target()                   # __ - "TOP:"
    label("top")                    # __ - "TOP:"
    wait(HIGH, gpio, PHI)           # 04 - Wait for PHI high                                                             0.5    0.5
    jmp(pin, "pico_write")          # 05 - RWB - Proc-R, Pico-W                                                          1.5    1.5
    label("pico_read")              # __ - !RWB - Proc-W, Pico-R
    set(pindirs, INPUT)             # 06 - Set pico to read, could move _in here with nop stall                          2.5    set [1] 3.5
    wait(LOW, gpio, PHI)            # 07 - Wait for PHI high                                                             0.5    nop [1] 5.5
    in_(pins, NIBBLE)               # 08 - Shift data from pins, 8-16 ns after falling edge (too late?!?!) {bugcheck}    1.5    in / wait 6.5 ; 7 cycles
    jmp("top")                      # 09 - JMP to top                                                                           ^^ would work for up to 8.9 MHz
    label("pico_write")             # __ - RWB - Proc-R, Pico-W
    set(pindirs, OUTPUT)            # 10 - Set pico to write
    out(pins, NIBBLE)               # 11 - Shift data to pins, 23-30ns after rising edge
    wait(LOW, gpio, PHI)            # 12 - Wait for PHI low
    wrap()                          # __ - JMP to top

# Create state machine for each data nibble to R/W.
sm_dn1 = StateMachine(4, pio_dn, in_base = DN1[0], out_base = DN1[0], set_base = DN1[0], jmp_pin = RWB[0],
    out_shiftdir = PIO.SHIFT_RIGHT, pull_thresh = len(DN1), in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(DN1) ) # do reversal outisde of SM
sm_dn0 = StateMachine(5, pio_dn, in_base = DN0[0], out_base = DN0[0], set_base = DN0[0], jmp_pin = RWB[0],
    out_shiftdir = PIO.SHIFT_RIGHT, pull_thresh = len(DN0), in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(DN0) ) # do reversal outisde of SM

# One bit version of the 4 bit data state machine.
@asm_pio(out_init=tuple([PIO.OUT_LOW] * len(DB0)), set_init=tuple([PIO.OUT_LOW] * len(DB0)), autopush = True, autopull = True)
def pio_db0():
    PHI = 28                        # PHI pin constant
    BIT = 1                         # Single BIT
    OUTPUT = HIGH = 1               # OUTPUT on 1 and "HIGH" level on 1
    INPUT = LOW = 0                 # INPUT on 0 and "LOW" level on 0

    wrap_target()                   # __ - "TOP:"
    label("top")                    # __ - "TOP:"
    wait(HIGH, gpio, PHI)           # 13 - Wait for PHI high
    jmp(pin, "pico_write")          # 14 - RWB - Proc-R, Pico-W
    label("pico_read")              # __ - !RWB - Proc-W, Pico-R
    set(pindirs, INPUT)             # 15 - Set pico to read
    wait(LOW, gpio, PHI)            # 16 - Wait for PHI low
    in_(pins, BIT)                  # 17 - Shift data from pins
    jmp("top")                      # 18 - JMP to top
    label("pico_write")             # __ - RWB - Proc-R, Pico-W
    set(pindirs, OUTPUT)            # 19 - Set pico to write
    out(pins, BIT)                  # 20 - Shift data to pins
    wait(LOW, gpio, PHI)            # 21 - Wait for PHI low
    wrap()                          # __ - JMP to top

# Create 1 bit data state machine
sm_db0 = StateMachine(6, pio_db0, in_base = DB0[0], out_base = DB0[0], set_base = DB0[0], jmp_pin = RWB[0],
    out_shiftdir = PIO.SHIFT_RIGHT, pull_thresh = len(DB0), in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(DB0)) # invert shift

# Combine RWB (ro) and PHI (wo) bits into last state machine, since we only have this last one left
@asm_pio(out_init = PIO.OUT_LOW, autopush = True)
def pio_phi_rwb():
    BIT = 1                         # BIT = 1 bit

    wrap_target()                   # __ - "TOP:"
    label("phi_high")               # __ - "HIGH:" where we jmp when we set the clock high
    pull()                          # 22 - Disable autopull so we can taste ISR
    mov(x, osr)                     # 23 - Save a copy of OSR in to X
    out(pins, BIT)                  # 24 - Shift PHI data to pins
    jmp(x, "phi_high")              # 25 - If we transitioned low to High, don't shift RWB
    label("phi_low")                # __ -
    in_(pins, BIT)                  # 26 - If we transitioned High to Low, read RWB and autopush OSR
    wrap()                          # __ - JMP to top

# Create state machine RWB and PHI
sm_phi_rwb = StateMachine(7, pio_phi_rwb, out_base = PHI[0], out_shiftdir = PIO.SHIFT_RIGHT,
                      in_base = RWB[0], in_shiftdir = PIO.SHIFT_LEFT, push_thresh = len(RWB)) # invert shift

# Send "RUN" command to all state mahcines
for sm in [sm_phi_rwb, sm_db0, sm_dn0, sm_dn1, sm_an0, sm_an1, sm_an2, sm_an3]:
    sm.active(1)


end = ticks_add(ticks_us(), USDELAY)  # end future sleep after DELAY microseconds
# CYCLES = 9000                       # stub code for timing tests
# tstart = ticks_us()                 # stub code for timing tests
try:
    #for i in range(0, CYCLES):       # stub code for timing tests
    while True:

        #  To perform a high clock cycle we need to do the following
        #     1. Drive PHI high
        #     2. Drive LED indicator high
        #     3. Read RWB and ADDRESS
        #     4. If RWB, provide data before falling edge
        #
        ############# CLOCK HIGH #############
        sleep_us(ticks_diff(end, ticks_us()))
        end = ticks_add(ticks_us(), USDELAY)
        sm_phi_rwb.put(1)
        LED.value(1)
        rwb = sm_phi_rwb.get()
        if rwb: # ProcR, PicoW
            data = DATA
            db0 = (DATA & 0b_0000_0001)
            dn0 = (DATA & 0b_0001_1110) >> 1
            dn1 = (DATA & 0b_1111_0000) >> 4
            sm_db0.put(db0)
            sm_dn0.put(rev[dn0])
            sm_dn1.put(rev[dn1])
        an0 = sm_an0.get()
        an1 = sm_an1.get() << 4
        an2 = sm_an2.get() << 8
        an3 = rev[sm_an3.get()] << 12
        address = an3 | an2 | an1 | an0

        #  To perform a low clock cycle we need to do the following
        #     1. Drive PHI low
        #     2. Drive LED indicator low
        #     3. If !RWB, grab data on falling edge
        #
        ############# CLOCK LOW #############
        sleep_us(ticks_diff(end, ticks_us()))
        end = ticks_add(ticks_us(), USDELAY)
        sm_phi_rwb.put(0)
        LED.value(0)
        if not rwb: # ProcW, PicoR
            db0 = sm_db0.get()
            dn0 = rev[sm_dn0.get()] << 1
            dn1 = rev[sm_dn1.get()] << 4
            data = dn1 | dn0 | db0

        # Display pin data then break if the BOOTSEL button is pressed
        print("{} Address: 0x{:04X} Data: 0x{:02X}".format("r" if rwb else "W", address, data))
        if REAL_HW and bootsel_button(): raise BootSelButton

except KeyboardInterrupt:
    print("Caught Stop Req")
except BootSelButton:
    print("Caught Stop Button")
except Exception as e:
    print(f"Opps... Unexpected error caught: {e}")

# tend = ticks_us()
# ms = ticks_diff(tend,tstart) / 1000
# KHz = CYCLES/ms
# print("KHz", KHz, "ms", ms)

print("done")

for sm in [sm_phi_rwb, sm_db0, sm_dn0, sm_dn1, sm_an0, sm_an1, sm_an2, sm_an3]:
    sm.active(0)
