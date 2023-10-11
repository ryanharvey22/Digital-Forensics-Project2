# Project2
#
# Ecample output:
#
# File1.mpg, Start Offset: 0x100000, End Offset: 0x200000 
# SHA-256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08 
#
# File2.pdf, Start Offset: 0x100000, End Offset: 0x200000 
# SHA-256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08 
#
# File3.gif, Start Offset: 0x100000, End Offset: 0x200000 
# SHA-256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08 
#
# File4.mpg, Start Offset: 0x100000, End Offset: 0x200000 
# SHA-256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08 
#
# File5.pdf, Start Offset: 0x100000, End Offset: 0x200000 
# SHA-256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08 
#
# Recovered files are located in ~/RecoveredFiles 

import sys
import os

class Partition:
    def __init__(self):
        pass

# calls hexdump for given range and puts offsets and bytes into respective lists.
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
                    exit()
        elif len(s) == 1:
            offsets.append(s[0])
            bytes.append(['']*16)
    return offsets, bytes

def find_ascii(str, dump:dict):
    for addr in dump:
        hex_string = ''.join([byte.hex() for byte in dump[addr]])
        hex_num = int(hex_string,16)
        print(hex_string)
        if hex_string.decode("ASCII").contains(str):
            return addr
    return -1
# get boot sector info


def get_diskinfo(disk) -> Partition():

    partition = Partition()

    # bytes come in hexdump format
    offsets, bytes = hexdump_to_list(disk, 0, 1)
    temp = bytes[0][11:13]
    partition.bytes_per_sector = int(''.join(temp[::-1]), 16)

    partition.sectors_per_cluster = int(bytes[0][13], 16)
    
    temp = bytes[0][14:]
    partition.reserved_sectors = int(''.join(temp[::-1]), 16)

    partition.num_FATs = int(bytes[1][0], 16)
    
    temp = bytes[1][3:5]
    partition.num_sectors = int(''.join(temp[::-1]), 16)
    
    temp = bytes[1][6:8]
    partition.num_sectors_per_FAT = int(''.join(temp[::-1]), 16)
    
    temp = bytes[1][12:]
    partition.num_sectors_before_partition = int(''.join(temp[::-1]), 16)

    return partition

info = get_diskinfo("Project2.dd")

print(info.bytes_per_sector)
print(info.sectors_per_cluster)
print(info.reserved_sectors)
print(info.num_FATs)
print(info.num_sectors)
print(info.num_sectors_per_FAT)
print(info.num_sectors_before_partition)
print()

sFAT = info.reserved_sectors
nFAT = info.num_sectors_per_FAT
sroot = info.reserved_sectors + info.num_sectors_per_FAT*2
nroot = 32

root = hexdump_to_list("Project2.dd", sFAT, nFAT)
FAT = hexdump_to_list("Project2.dd", sFAT, nFAT)

