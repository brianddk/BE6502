# Raspberry Pi Pico

In most of the BE6502 lessons, an Arduino Mega is used.  But for some other work I needed to do I had a Pi Pico and PiZero.
Lucilly both the Pico and the Zero come with 26 available GPIOs, so that is enough for RWB, PHI, ADDRESS and DATA.
This allowed me to emulate the work of the Mega on the Pico using Micropython instead of Arduino Sketch.
If your a big Sketch fan, I know it will run on Pico as well, but I'll focus on Micropython instead.

## Quick setup

Here's the quickest setup I can think of.

1. Download Micropython U2F file for either the [Pico][mp-pico] or [Pico W][mp-picow]
2. Hold down BOOTSEL button on the pico and plug it into a computer
3. Drop the U2F file onto the drive that appeared after plugging it in
4. Install [mpremote][mp-rmt] from pip: `pip install mpremote`
5. Install [Thonny][thonny] which is a GUI with mpremote built in.
6. Run the files using `mpremote run file.py` or interactively with ***Thonny***
7. To install persistantly copy it as *main.py*: `mpremote cp file.py :main.py`
8. To remove persistant copy: `mpremote rm main.py`

## Reference Material

1. [Pico Documentation Hub][pico-doc]
2. [Micropython Documentation][mp-doc]
3. [Pico's PIO assembler][pio-doc]

## Files

Note, these files have the 6502 hooked to a 3V3 rail instead of a 5V rail.  I got a bunch of [Ti CD4504B's][cd4504b] that convert from 5V to 3V3 for me.
If I don't sample any bus data, I can generate a 5V clock at pretty much any speed between from 1 Hz to 66.5 MHz.
Finally, the purpose of the Video #20 serial terminal is based on the simple fact that I don't own a USB RS-232 adapter.
Simple to just drop in at the UART before the voltages get stepped up to RS-232 ranges.
Of course I have another PiZero I could use to do it, but thought it would be fun to make one for the Pico.

1. [vid1-t1195.py](vid1-t1195.py) - Micropython example to perform the Arduino work shown at 19:55 in [Video #01][vid1]
2. [vid1-t1195-pio.py](vid1-t1195-pio.py) - Pico PIO assmbler example to perform the Arduino work shown at 19:55 in [Video #01][vid1]
3. [vid20-t1034.py](vid20-t1034.py) - Micropython example to work as a serial terminal at 17:14 in [Video #20][vid20]

[mp-pico]: https://micropython.org/download/RPI_PICO/
[mp-picow]: https://micropython.org/download/RPI_PICO_W/
[mp-rmt]: https://pypi.org/project/mpremote/
[thonny]: https://thonny.org/
[pico-doc]: https://www.raspberrypi.com/documentation/microcontrollers/
[mp-doc]: https://docs.micropython.org/en/latest/
[pio-doc]: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=310
[vid1]: https://youtu.be/LnzuMJLZRdU?t=1195
[vid20]: https://youtu.be/oLYLnb7kpLg?t=1034
[cd4504b]: https://www.ti.com/lit/ds/symlink/cd4504b-mil.pdf
