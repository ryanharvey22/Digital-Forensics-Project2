import sys
import os
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

sroot = reserved_sectors + num_sectors_per_FAT*2
nroot = 32
offset_root, bytes_root = hexdump_to_list(DISK, sroot, nroot)

file_lengths = []
file_allocated = []
file_names = []
file_extensions = []
i = 1
while i < len(bytes_root) - 2:
    # if ''.join(bytes_root[i][14:]) == '0000':  # EOS # 1-9, 9-12
    if bytes_root[i+1][0] in ['e5','2e','51'] and bytes_root[i+2][0] != "ff":
        # Get File Name
        file_nameBytes = (bytes_root[i+1][1:11])
        file_nameBytes+= (bytes_root[i+1][14:16])
        file_nameBytes+= (bytes_root[i+2][0:10])
        
        file_name = ""
        index = 0
        while index < len(file_nameBytes)-1:
            try:
                string = file_nameBytes[index]
                newString = codecs.decode(string, "hex").decode("ASCII")
                if "0f" not in string:
                    file_name += newString
                index +=2
            except:
                index+=1
                pass

        file_names.append(file_name.split('.')[0])

        # Get File Extension
        ext = bytes_root[i+3][8:11]
        try:
            ext = codecs.decode(''.join(ext), "hex").decode("ASCII")
            file_extensions.append(ext.lower())
        except:
            file_extensions.append(f"File{i}")

        # Get File size in hex from root dir and convert to an integer
        file_size = bytes_root[i+4][12:16]
        hex_string = file_size[3] + file_size[2] + file_size[1] + file_size[0]
        file_sizeInt = int(hex_string, 16)

        # Find size in sectors
        file_sizeInt = math.ceil(file_sizeInt/512)
        # Find total allocated sectord
        total_allocated = math.ceil(file_sizeInt / sectors_per_cluster) * sectors_per_cluster

        file_lengths.append(file_sizeInt)
        file_allocated.append(total_allocated)

        # Move to next entry
        i += 4    
    elif bytes_root[i+2][0] == "ff":
        # skip this false entry
        i+=2
    else:
        # check next line
        i += 1

# Start of data section = disk information sectors (sectors before partition) + reserved sectors + 1st fat + ... nFat + root directory (32) + offset (count found above -2)
data_starts =   8 + reserved_sectors + (num_sectors_per_FAT * num_FATs) + 32 + (sectors_per_cluster * (count -2))

offsets = []
for i in range(len(file_lengths)):
    if i == 0:
        start = data_starts
    else:
        start = offsets[i-1][0] + (file_allocated[i-1])
    end = start + file_lengths[i]
    offsets.append([start, end])



#############################################
#   Displaying Results to the command line  #
#############################################
file_signatures = [
    ("jpg", ['ff', 'd8', 'ff', 'e0'], ['ff', 'd9']),
    ("jpg", ['ff', 'd8', 'ff', 'e1'], ['ff', 'd9']),
    ("jpg", ['ff', 'd8', 'ff', 'e8'], ['ff', 'd9']),
    ("jpg", ['ff', 'd8'], ['ff', 'd9']),
    ("mpg", ['00', '00', '01', 'ba'], ['00', '00', '01', 'b9']),
    ("mpg", ['00', '00', '01', 'b3'], ['00', '00', '01', 'b7']),
    ("gif", ['47', '49', '46', '38', '37', '61'], ['00', '3b']),
    ("gif", ['47', '49', '46', '38', '39', '61'], ['00', '3b']),
    ("docx",['50', '4b', '03', '04', '14', '00', '06', '00'],['50', '4b', '05', '06']),
    ("avi", ['41', '56', '49', '20', '4c', '49', '53', '54'], []),
    ("png", ['89', '50', '4e', '47', '0d', '0a', '1a', '0a'], ['49', '45', '4e', '44', 'ae', '42', '60', '82']),
    ("pdf", ['25', '50', '44', '46'], ['25', '25', '45', '4f', '46']),
    ("bmp", ['42','4d'], []),
]

if not os.path.exists("RecoveredFiles"):
    os.mkdir("RecoveredFiles")
for i in range(len(offsets)):
    skip = offsets[i][0]
    length = file_lengths[i]
    file_name = file_names[i]
    print()
    signatureOffsets, bytes_signature = hexdump_to_list(DISK, skip, 1)
    print(f"File Signature: {bytes_signature[0]}")  
    index = 0
    matches = ""
    while index < len(file_signatures):
        if (''.join(file_signatures[index][1]) in ''.join(bytes_signature[0])):
            matches = file_signatures[index][0]
            index = len(file_signatures)
        index+=1

    os.system(f"dd if={DISK} of=RecoveredFiles/{file_name}.{matches} bs={bytes_per_sector} skip={skip} count={length} status=none")
    temp = os.popen(f"shasum -a 256 RecoveredFiles/{file_name}.{matches}")
    shasum = os.popen(f"shasum -a 256 RecoveredFiles/{file_name}.{matches}").read().split()[0]
    print(f"{file_name}.{matches}, Start Offset: {skip}, End Offset: {skip+length}")
    print("SHA-256: ", shasum)
    
print()