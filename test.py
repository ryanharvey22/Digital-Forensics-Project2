import os

DISK = "Project2.dd"

file_signatures = [
    ("mpg", ['00', '00', 0x01, 0xBA], [0xff, 0xD9]),
    ("pdf", [0x25, 0x50, 0x44, 0x46], [0xff, 0xD9]),
    ("bmp", [0x42, 0x4F, 0x4F, 0x4B, 0x4D, 0x4F, 0x42, 0x49], [0xff, 0xD9]),
    ("gif", [0x47, 0x49, 0x46, 0x38, 0x37, 0x61], [0xff, 0xD9]),
    ("jpg", [0xFF, 0xD8, 0xFF, 0xE0], [0xff, 0xD9]),
    ("docx",[],[0xff, 0xD9]),
    ("avi", [],[0xff, 0xD9]),
    ("png", [],[0xff, 0xD9]),
]

sig_heads = [
    ['00', '00', '01', 'BA'], 
    ['25', '50', '44', '46'], 
    ['42', '4F', '4F', '4B', '4D', '4F', '42', '49'], 
    ['47', '49', '46', '38', '37', '61'],
    ['FF', 'D8', 'FF', 'E0']
]

sig_foots =  [
    [0xff, 0xD9],
    [0xff, 0xD9],
    [0xff, 0xD9],
    [0xff, 0xD9],
    [0xff, 0xD9]
]

def hexdump_to_list(disk, start_sector, skip_sector):
    output = os.popen(f"hexdump -s $(({start_sector}*512)) -n $(({skip_sector}*512)) {disk}").read().split("\n")
    bytes = []
    offsets = []
    for i, line in enumerate(output):

        s = line.split()
        if len(s) > 1:
            for x in s:
                if len(x) > 4:
                    offsets.append(x)
                elif len(x) == 4:
                    bytes.append(x[2:4])
                    bytes.append(x[0:2])
                else:
                    print("Error processing bytes")
                    exit(1)
        elif len(s) == 1:
            offsets.append(s[0])
            for i in range(16):
                bytes.append('')
    return offsets, bytes

data_section = hexdump_to_list(DISK, 448, 5000)
byte_data = data_section[1]
print(len(byte_data))
for w in range(len(sig_heads)):
    #print("checking: ", sig_heads[w])
    for i in range(len(byte_data)):
        #print("agaisnt ", byte_data[i:i+len(sig_heads[w])])
        if sig_heads[w] == byte_data[i:i+len(sig_heads[w])]:
            print("found head at", w)
        if sig_foots[w] == byte_data[i:i+len(sig_foots[w])]:
            print("found foot at ", w)