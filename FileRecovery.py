import sys
import os
import hashlib
import math
import codecs

print("Checking Dependencies")
if len(sys.argv) == 2:
    DISK = sys.argv[1]
elif len(sys.argv) < 2:
    # print("Error, Please provide disk")
    # exit(1)
    DISK = "Project2.dd"
else:
    print("Error, Provided too many arguments. Ignoring extra")



############################################################################
#   Function to ask machine for DISK bytes and offsets using hexdump tool  #
############################################################################
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


# bytes come in hexdump format
offsets, bytes_boot = hexdump_to_list(DISK, 0, 1)
bytes_per_sector = int(''.join(bytes_boot[0][11:13][::-1]), 16)
sectors_per_cluster = int(bytes_boot[0][13], 16)
reserved_sectors = int(''.join(bytes_boot[0][14:][::-1]), 16)
num_FATs = int(bytes_boot[1][0], 16)
num_sectors = int(''.join(bytes_boot[1][3:5][::-1]), 16)
if num_sectors == 0:
    num_sectors = 65535 # OK this is definitly wrong because algorithm gets a higher offset
num_sectors_per_FAT = int(''.join(bytes_boot[1][6:8][::-1]), 16)
num_sectors_before_partition = int(''.join(bytes_boot[1][12:][::-1]), 16)
sFAT = reserved_sectors
nFAT = num_sectors_per_FAT
offset_FAT1, bytes_FAT1 = hexdump_to_list(DISK, sFAT, nFAT)



###################################
#   Make List of file extentions  #
###################################
file_signatures = [
    # (ext, header,..., footer)
    ("mpg", [0x00, 0x00, 0x01, 0xBA], [0xff, 0xD9]),
    ("pdf", [0x25, 0x50, 0x44, 0x46], [0xff, 0xD9]),
    ("bmp", [0x42, 0x4F, 0x4F, 0x4B, 0x4D, 0x4F, 0x42, 0x49], [0xff, 0xD9]),
    ("gif", [0x47, 0x49, 0x46, 0x38, 0x37, 0x61], [0xff, 0xD9]),
    ("jpg", [0xFF, 0xD8, 0xFF, 0xE0], [0xff, 0xD9]),
    ("docx",[],[0xff, 0xD9]),
    ("avi", [],[0xff, 0xD9]),
    ("png", [],[0xff, 0xD9]),
]
sroot = reserved_sectors + num_sectors_per_FAT*2
nroot = 32
offset_root, bytes_root = hexdump_to_list(DISK, sroot, nroot)

# lets change this to use the hex signatures, go by four and look for header and footer?
file_names = []
for i in range(len(bytes_root)):
    if ''.join(bytes_root[i][14:]) == '0000':  # EOS # 1-9, 9-12
        if bytes_root[i+1][0] in ['00','e5','2e','51']:
            name, ext = bytes_root[i+1][1:9], bytes_root[i+1][9:12]

exts_test = ["jpg", "avi", "pdf", "png", "jpg", "bmp", "pdf", "jpg", "jpg", "gif", "avi", "docx", "mpg"]






##############################################################
#   Finds and sets the starting offset for the data section  #
##############################################################
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


#######################################
#   Finds File Lengths from root dir  #
#######################################

file_lengths = []
file_allocated = []
file_names = []
i = 1
while i < len(bytes_root) - 1:
    # if ''.join(bytes_root[i][14:]) == '0000':  # EOS # 1-9, 9-12
    if bytes_root[i+1][0] in ['e5','2e','51']:
        file_size = bytes_root[i+4][12:16]
        hex_string = file_size[3] + file_size[2] + file_size[1] + file_size[0]
        file_sizeInt = int(hex_string, 16)
        total_allocated = math.ceil(file_sizeInt / sectors_per_cluster) * sectors_per_cluster
        file_name = ''.join(bytes_root[i+1][1:16])
        # the below code is throwing an error because the Auburn file has 96 in the file name, which is not ascii
        # need to somehow skip this (and remove the hex before it as well)
        # file_name = codecs.decode(''.join(file_name), "hex").decode("ASCII")
        file_lengths.append(file_sizeInt)
        file_allocated.append(total_allocated)
        file_names.append(file_name)
        i += 4    
    else:
        i += 1

# Start of data section = disk information sectors (sectors before partition) + reserved sectors + 1st fat + ... nFat + root directory (32) + offset (count found above -2)
data_starts = num_sectors_before_partition + reserved_sectors + (num_sectors_per_FAT * num_FATs) + 32 + (sectors_per_cluster * (count -2))



#############################
#   Finds Offsets of files  #
#############################
count = -count
files = [(0, int(offset_FAT1[0]))]
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




#############################################
#   Displaying Results to the command line  #
#############################################
if not os.path.exists("RecoveredFiles"):
    os.mkdir("RecoveredFiles")
for i in range(len(files) - 1):
    skip =  reserved_sectors + num_sectors_per_FAT * 2 + 32 + files[i][0] * sectors_per_cluster
    length = (files[i+1][0] - files[i][0]) * sectors_per_cluster
    #print(f"skip={skip}, count={length}")
    os.system(f"dd if={DISK} of=RecoveredFiles/File{i+1}.{exts_test[i]} bs={bytes_per_sector} skip={skip} count={length} status=none")
    temp = os.popen(f"shasum -a 256 RecoveredFiles/File{i+1}.{exts_test[i]}")

    shasum = os.popen(f"shasum -a 256 RecoveredFiles/File{i+1}.{exts_test[i]}").read().split()[0]
    print(f"\nFile{i+1}.{exts_test[i]}, Start Offset: {skip}, End Offset: {skip+length}")
    print("SHA-256: ", shasum)
    
print()