# 6502 Analyzer

This analyzer will track 8 data pins, 16 address pins, one RW pin, and produce 1 clock pin, 26 pins in total.  
Neither of my SoCs will monitor that many signals, but if I network them I can get there.
The [Raspberry Pi 1 Model B (512)](rpi1_modb_rev2.md) has 17 GPIOs so it will produce the clock and monitor the 8 data pins.  
The [ODROID C1+](odroid_c1.md) will monitor the address pins and RW pin.
Both SoCs 

