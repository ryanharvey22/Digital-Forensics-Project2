import os
import sys
import time

DISK = sys.argv[1]

sigs = [
    "\x89\x50\x4E\x47\x0D\x0A\x1A\x0A",
    "\x25\x50\x44\x46",
    "\x42\x4D",
    "\x47\x49\x46\x38\x37\x61",
    "\x49\x46\x38\x39\x61",
    "\xFF\xD8\xff\xE0",
    "\x50\x4B\x03\x04\x14\x00\x06\x00",
    "\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
]

def hexdump_to_list(disk, start_sector, skip_sector):
    output = os.popen(f"hexdump -s $(({start_sector}*512)) -n $(({skip_sector}*512)) {disk}").read().split("\n")
    bytes = []
    offsets = []
    for i, line in enumerate(output):
        s = line.split()
        if len(s) > 1:
            bytes.append([])
            for x in s:
                if len(x) > 4:
                    offsets.append(x)
                elif len(x) == 4:
                    bytes[i].append(x[2:4])
                    bytes[i].append(x[0:2])
                else:
                    print("Error processing bytes")
                    exit(1)
        elif len(s) == 1:
            offsets.append(s[0])
            bytes.append(['']*16)
    return offsets, bytes

offsets, bytes_boot = hexdump_to_list(DISK, 0, 1)
reserved_sectors = int(''.join(bytes_boot[0][14:][::-1]), 16)
num_secotrs_per_FAT = num_sectors_per_FAT = int(''.join(bytes_boot[1][6:8][::-1]), 16)
num_FATs = int(bytes_boot[1][0], 16)
bytes_per_sector = int(''.join(bytes_boot[0][11:13][::-1]), 16)
num_sectors = int(''.join(bytes_boot[1][3:5][::-1]), 16)
if num_sectors == 0:
    num_sectors = 65535

start_of_data = reserved_sectors + num_sectors_per_FAT * num_FATs + 32

for i in range(len(sigs)):
    os.system(f"dd if={DISK} bs={bytes_per_sector} skip={start_of_data} count={num_sectors-start_of_data} status=none | binwalk -R \"{sigs[i]}\" -")
    time.sleep(3)

# put DATA into combined file
#start_of_data = reserved_sectors + num_sectors_per_FAT * 2 + 32
#os.system(f"dd if={DISK} of=combinedFiles bs={bytes_per_sector} skip={start_of_data} count={num_sectors-start_of_data} status=none")

# 8 + 400 + 32 :: dd if=Project2.dd of=combinedFiles bs=512 skip=440 count= status=none