#!/home/pi/src/WiringPi-Python/.venv/bin/python3
# [CDN] https://pypi.org/project/wiringpi/2.60.1/
# [SRC] https://github.com/WiringPi/WiringPi-Python/

from wiringpi import wiringPiSetup, pinMode, digitalWrite, OUTPUT, HIGH, LOW
from time import sleep
from sys import argv

PHASE2 = LOW
PHASE1 = HIGH
CLOCK  = 6
Hz     = 1            # Caps out at about 3_000 Hz (3kHz)
delay  = 0.5 * 1/Hz

# One of the following MUST be called before using IO functions:
wiringPiSetup()          # For sequential pin numbering
pinMode(CLOCK, OUTPUT)   # Set pin 6 to 1 ( OUTPUT )
ticks = 0

nonstop = halfstep = quiet = False
if len(argv) > 1:
    if argv[1] == '-n': nonstop  = True
    if argv[1] == '-i': halfstep = True
    if argv[1] == '-q': quiet = nonstop = True

print("6502 starts the clock on the falling edge (phase 1) and finishes on the rising edge (phase 2)")
try:
    while(True):
        digitalWrite(CLOCK, PHASE2)
        if not quiet:
            print(f"TICK {ticks}.5: clock (pin{CLOCK}) in PHASE2 (digital {PHASE2})")
        if nonstop:
            sleep(delay)
        else:
            input("Press any key to advance")
        ticks += 1
        digitalWrite(CLOCK, PHASE1)
        if not quiet:
            print(f"TICK {ticks}.0: clock (pin{CLOCK}) in PHASE1 (digital {PHASE1})")
        if halfstep:
            input("Press any key to advance")
        else:
            sleep(delay)
except KeyboardInterrupt:
    digitalWrite(CLOCK, PHASE2)
    print(f"TICK {ticks}: clock (pin{CLOCK}) in PHASE2 (digital {PHASE2})")

