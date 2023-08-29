#
# Please see this video for details:
# https://www.youtube.com/watch?v=yl8vPW5hydQ
#
# https://skilldrick.github.io/easy6502/
# 
head = bytearray([
    0xa9, 0xff,         # lda #$ff
    0x8d, 0x02, 0x60,   # sta $6002
    
    0xa9, 0x0f,         # lda #$0f
    0x18,               # clc

# $8008:
    0x8d, 0x00, 0x60,   # sta $6000
    ])

# nops

tail = bytearray([
    0x2a,               # rol A
    0x4c, 0x08, 0x80,   # jmp $8008

    0x00, 0x80,         # reset vector
    0xea, 0xea,         # fill
    ])

nops = 2**15 - len(head) - len(tail)
rom = head + bytearray([0xea] * nops) + tail

with open("rom.bin", "wb") as out_file:
    out_file.write(rom)

# 0 0000 1111
# 0 0001 1110
# 0 0011 1100
# 0 0111 1000
# 0 1111 0000
# 1 1110 0000
# 1 1100 0001
# 1 1000 0011
# 1 0000 0111
# 0 0000 1111
#
# 4 on / 5 off

on = 4 * nops * 2 / 1_000_000
off = 5 * nops * 2 / 1_000_000
hz = 1/(on+off)

print(f"{hz} Hz blink rate")
