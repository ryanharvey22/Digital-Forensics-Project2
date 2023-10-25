import sys
import os
import hashlib

print("Checking Dependencies")
if sys.platform != "linux":
    print(os.system("binwalk"))

if len(sys.argv) == 2:
    DISK = sys.argv[1]
elif len(sys.argv) < 2:
    # print("Error, Please provide disk")
    # exit(1)
    DISK = "Project2.dd"
else:
    print("Error, Provided too many arguments. Ignoring extra")

FILE_SIGS = {
    "\x89\x50\x4E\x47\x0D\x0A\x1A\x0A" : "MPG",
    "\x25\x50\x44\x46" : "PDF",
    "\x42\x4D" : "BMP",
    "\x47\x49\x46\x38\x37\x61" : "GIF",
    "\x49\x46\x38\x39\x61" : "GIF",
    "\xFF\xD8\xff\xE0" : "JPG",
    "\x50\x4B\x03\x04\x14\x00\x06\x00": "DOCX",
    " " : "AVI",
    "\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "PNG"
}

array = ["\x89\x50\x4E\x47\x0D\x0A\x1A\x0A", "\x25\x50\x44\x46", "\x42\x4D"]

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


# bytes come in hexdump format
offsets, bytes_boot = hexdump_to_list(DISK, 0, 1)
temp = bytes_boot[0][11:13]
bytes_per_sector = int(''.join(temp[::-1]), 16)

sectors_per_cluster = int(bytes_boot[0][13], 16)

temp = bytes_boot[0][14:]
reserved_sectors = int(''.join(temp[::-1]), 16)

num_FATs = int(bytes_boot[1][0], 16)

temp = bytes_boot[1][3:5]
num_sectors = int(''.join(temp[::-1]), 16)
if num_sectors == 0:
    num_sectors = 65535

temp = bytes_boot[1][6:8]
num_sectors_per_FAT = int(''.join(temp[::-1]), 16)

temp = bytes_boot[1][12:]
num_sectors_before_partition = int(''.join(temp[::-1]), 16)


sFAT = reserved_sectors
nFAT = num_sectors_per_FAT
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

sroot = reserved_sectors + num_sectors_per_FAT*2
nroot = 32
offset_root, bytes_root = hexdump_to_list(DISK, sroot, nroot)

# lets change this to use the hex signatures, go by four and look for header and footer?
file_names = []
for i in range(len(bytes_root)):
    if ''.join(bytes_root[i][14:]) == '0000':  # EOS # 1-9, 9-12
        if bytes_root[i+1][0] in ['00','e5','2e','51']:
            name, ext = bytes_root[i+1][1:9], bytes_root[i+1][9:12]
            file_names.append(hex_list_to_ascii(name) + "." + hex_list_to_ascii(ext))

# start_of_data = reserved_sectors + num_sectors_per_FAT * 2 + 32
# os.system(f"dd if={DISK} of=RecoveredFiles/File{i+1}.jpg bs={bytes_per_sector} skip={skip} count={length} status=none")
# os.system(f"binwalk -R '\x25\x50\x44\x46' ")

exts_test = ["jpg", "avi", "pdf", "png", "jpg", "bmp", "pdf", "jpg", "jpg", "gif", "avi", "docx", "mpg"]

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
