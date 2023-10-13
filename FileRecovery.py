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

if len(sys.argv) == 2:
    DISK = sys.argv[1]
elif len(sys.argv) < 2:
    # print("Error, Please provide disk")
    # exit(1)
    DISK = "Project2.dd"
else:
    print("Error, Provided too many arguments. Ignoring extra")

class Struct:
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
                    exit(1)
        elif len(s) == 1:
            offsets.append(s[0])
            bytes.append(['']*16)
    return offsets, bytes

def hex_list_to_ascii(x:list) -> str:
    output = ""
    for i in x:
        output += chr(int(i, 16))
    return output


info = Struct()

# bytes come in hexdump format
offsets, bytes_boot = hexdump_to_list(DISK, 0, 1)
temp = bytes_boot[0][11:13]
info.bytes_per_sector = int(''.join(temp[::-1]), 16)

info.sectors_per_cluster = int(bytes_boot[0][13], 16)

temp = bytes_boot[0][14:]
info.reserved_sectors = int(''.join(temp[::-1]), 16)

info.num_FATs = int(bytes_boot[1][0], 16)

temp = bytes_boot[1][3:5]
info.num_sectors = int(''.join(temp[::-1]), 16)

temp = bytes_boot[1][6:8]
info.num_sectors_per_FAT = int(''.join(temp[::-1]), 16)

temp = bytes_boot[1][12:]
info.num_sectors_before_partition = int(''.join(temp[::-1]), 16)


sFAT = info.reserved_sectors
nFAT = info.num_sectors_per_FAT
offset_FAT1, bytes_FAT1 = hexdump_to_list(DISK, sFAT, nFAT)

# first find sectors before first data in data section

count = 0
found_start = False
for i in range(len(bytes_FAT1)):
    for j in range(0, len(bytes_FAT1[0]), 2):
        if ''.join(bytes_FAT1[i][j:j+2]) == 'ffff' or ''.join(bytes_FAT1[i][j:j+2]) == 'f8ff':
            count += 1
        else:
            found_start = True
            break
    if found_start:
        break

count = -count
files = [(0, offset_FAT1[0])]
found_end = False
for i in range(len(bytes_FAT1)):
    for j in range(0, len(bytes_FAT1[0]), 2):
        if count >= 0:
            if ''.join(bytes_FAT1[i][j:j+2]) == "ffff":
                try:
                    found_end = bytes_FAT1[i][j+3] == "ff"
                except:
                    found_end = bytes_FAT1[i+1][0] == "ff"
                files.append((count, int(offset_FAT1[i], 16) + j))
                if found_end:
                    break
        count += 1
    if found_end:
        break


sroot = info.reserved_sectors + info.num_sectors_per_FAT*2
nroot = 32
offset_root, bytes_root = hexdump_to_list(DISK, sroot, nroot)

file_names = []
for i in range(len(bytes_root)):
    if ''.join(bytes_root[i][14:]) == '0000':  # EOS # 1-9, 9-12
        if bytes_root[i+1][0] in ['00','e5','2e','51']:
            name, ext = bytes_root[i+1][1:9], bytes_root[i+1][9:12]
            file_names.append(hex_list_to_ascii(name) + "." + hex_list_to_ascii(ext))

print("\nfound file names:\n")
for file in file_names:
    print("\t"+file)

if not os.path.exists("RecoveredFiles"):
    os.mkdir("RecoveredFiles")
for i in range(len(files) - 1):
    skip =  info.reserved_sectors + info.num_sectors_per_FAT * 2 + 32 + files[i][0] * info.sectors_per_cluster
    length = (files[i+1][0] - files[i][0]) * info.sectors_per_cluster
    print(f"skip={skip}, count={length}")
    os.system(f"dd if={DISK} of=RecoveredFiles/File{i+1}.jpg bs={info.bytes_per_sector} skip={skip} count={length} status=none")