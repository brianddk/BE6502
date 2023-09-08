# 6502 Analyzer

This analyzer will track 8 data pins, 16 address pins, one RW pin, and produce 1 clock pin, 26 pins in total.  
Neither of my SoCs will monitor that many signals, but if I network them I can get there.
The [Raspberry Pi 1 Model B (512)](rpi1_modb_rev2.md) has 17 GPIOs so it will produce the clock and monitor the 8 data pins.  
The [ODROID C1+](odroid_c1.md) will monitor the address pins and RW pin.
Both SoCs 

# Steps for the Pi

- Burn OS 
- Place `lastip.sh`, `gpg_key.sec`, `gpg_key.pub`, `ssh_key.pub`, and `data.sec.gpg` on boot fat.
- Boot OS
- Install `scdeamon` and add `gpg_key.sec`
- Disconnect network
- Move `lastip.sh` to `/usr/local/bin`
- Add `@reboot /usr/local/bin/lastip.sh` using `sudo crontab -e`
- Decrypt `secdata.asc` and set password approriately
- [Add SSH key][1] to RPi using `gpg_key.sec`
- [Disable SSH passwords][2] to secure server
- Reboot and reconnect network
- Optionally [upgrade to bookworm][3]
- Python3 `python3-dev python3-setuptools python3-pip python3-wheel python3-venv`
- Dev `build-essential pkg-config git libusb-1.0-0-dev swig wiringpi`
- Clone: `clone --recursive https://github.com/brianddk/BE6502.git ~/src/BE6502`
- VENV: `cd ~/src/BE6502/piControl/depends/wiringpi && python3 -m venv .venv`
- PIP: `source .venv/bin/activate && python3 -m pip install --upgrade pip setuptools wheel`
- WiringPi: `python3 -m pip install wiringpi==2.60.1`
- VASM: `cd ~/src/BE6502/piControl/depends/vasm && make CPU=6502 SYNTAX=oldstyle`
- Install: `sudo install -m 755 vasm6502_oldstyle /usr/local/bin/`
- Link: `cd /usr/local/bin && sudo ln -s vasm6502_oldstyle vasm`
- MiniPro: `cd ~/src/BE6502/piControl/depends/minipro && make && sudo make install`

[1]: https://linuxhandbook.com/add-ssh-public-key-to-server/ (add ssh key)
[2]: https://linuxhandbook.com/ssh-disable-password-authentication/ (disable password)
[3]: https://raspberrytips.com/update-raspberry-pi-latest-version/ (upgrade to bookworm)

# Packages

- gnu smartcard: `gnupg pcscd scdaemon pcsc-tools`
- minipro dev: `build-essential pkg-config git`
- wiringpro dev: `libusb-1.0-0-dev swig wiringpi`
- python dev: `python3-dev python3-setuptools python3-pip python3-wheel python3-venv`

# Documentation

- https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

# Level-shifter

- https://electronics.stackexchange.com/q/286820
- https://learn.sparkfun.com/tutorials/logic-levels/all
- https://www.allaboutcircuits.com/textbook/digital/chpt-3/logic-signal-voltage-levels/

# USB Power

- https://www.addictedtotech.net/best-powered-usb-hub-for-raspberry-pi-4-in-2021/
- http://www.chipprogrammer.info/tl866ii-plus-usb-chip-programmer/
- https://raspberrypi.stackexchange.com/a/2058/43868
- https://web.archive.org/web/20140331044851/http://www.raspberrypi.org/archives/1929
- https://www.raspberrypi.com/documentation/computers/config_txt.html#max_usb_current
