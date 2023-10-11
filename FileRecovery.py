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

    os.system(f"hexdump -C -s $((0*512)) -n $((1*512)) {disk_file}")
    output = os.popen(f"hexdump -s $((0*512)) -n $((1*512)) {disk_file}").read().split("\n")
    bytes = {}

    for line in output:
        
        s = line.split()

        if len(s) > 1:
            ls = []
            for x in s[1:]:
                if len(x) == 4:
                    ls.append(x[0:2])
                    ls.append(x[2:4])
                else:
                    print("Error processing bytes")
                    exit()
            bytes[s[0]] = ls

        elif len(s) == 1:
            bytes[s[0]] = None

    return bytes

def get_boot_sector(s):
    pass

print(dump_to_string("Project2.dd"))