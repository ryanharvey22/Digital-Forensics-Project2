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

def dump_to_string(disk_file):

    output = os.popen(f"hexdump -s $((0*512)) -n $((1*512)) {disk_file}").read().split()
    bytes = {}

    i = 0
    print(output)
    print()
    for _ in output:
        if len(output[i]) == 7:
            bytes[output[i]] = []
            for four in output[i+1:i+8]:
                if len(four) == 4:
                    bytes[output[i]].append(four[0:2])
                    bytes[output[i]].append(four[2:4])
                else:
                    print("Error processing bytes")
                    exit()
        else:
            print("Error, should by address part")

        i = i + 9
        
    return bytes

def get_boot_sector(disk_file):
    pass

print(dump_to_string("Project2.dd"))