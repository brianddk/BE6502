# Raspberry Pi Recovery Info

- MAC: b8:27:eb:5f:33:5d
- Avahi IP: 169.254.195.197 (from ZBook)
- Image: [2023-05-03-raspios-buster-armhf.img.xz](
https://downloads.raspberrypi.org/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2023-05-03/2023-05-03-raspios-buster-armhf-lite.img.xz
) ([archive](
https://web.archive.org/web/20230716102401/https://downloads.raspberrypi.org/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2023-05-03/2023-05-03-raspios-buster-armhf-lite.img.xz
))
- Image SHA256: `3d210e61b057de4de90eadb46e28837585a9b24247c221998f5bead04f88624c`
- Hostname: analyzer
- UserID/PW: **stored under hostname**

### Basic config information

- `crontab -e` to add `lastip.sh` to produce `lastip.log` in this location
- Modified `config.txt` to set GPU mem from 64 MB to 16 MB
- Basic `apt-update` and `apt-upgrade` commands
- Apt `python3-dev python3-setuptools swig wiringpi build-essential git python3-venv python3-pip`
- Git clone `https://github.com/WiringPi/WiringPi-Python.git`
- VENV: `python3 -m venv .venv` && `pip3 install --upgrade pip setuptools wheel`
- VENV: `pip3 install wiringpi`

```
-----BEGIN PGP MESSAGE-----

hQEMAxknaFN8ZgFHAQf/bLYmjNyTXhOKISooybAmGzHfOSyOUquWcR5NfNc+vt2R
xzELl3S4eYYvj8D6Ua3Al6Ub7OxHT3+yqEHzoMMTDv0+WIa1saMSIO4IP/tCc3oJ
ku92+ScC7xmquGfYMHfhFb7GcucvMTb+BwC/Q++xYJZtT3Vfdj2UXasTms8C8NgB
XAowTcK/YVMWBBIwce+UFzA6TXJ0ibZx5MuNcGmzZFi6Sdf25wUTf3EyLxRVnz9G
7voy+KSAD+p3E0w/T/ItSGdsOqEAgV3dfBwgh7ghHCsPL/wHmsmiBtrXe7fCl58S
BghrxjI5fzQobJ2BprtK13cMQh6jOPShzjTGKwBXNNJnARetuKGjfogHknCztOep
hc4nn3vaoXJ4G08X3Dl6UR23ntSpfo1OvSOhtnZYhOBxdlE9Q71e6MgYrVskMSZm
kBcGeUJ+uTl8A392v6ytVG1dZN+uTvc2sprK8LJfsYU+rJkza/qluw==
=o4Mo
-----END PGP MESSAGE-----
```
