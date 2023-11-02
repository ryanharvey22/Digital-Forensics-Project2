import os

DISK = "Project2.dd"

file_signatures = [
    ("jpg", ['ff', 'd8', 'ff', 'e0'], ['ff, d9']),
    ("jpg", ['ff', 'd8', 'ff', 'e1'], ['ff, d9']),
    ("jpg", ['ff', 'd8', 'ff', 'e8'], ['ff, d9']),
    ("jpg", ['ff', 'd8'], ['ff, d9']),
    ("mpg", ['00', '00', '01', 'ba'], ['00', '00', '01', 'b9']),
    ("mpg", ['00', '00', '01', 'bX'], ['00', '00', '01', 'b7']),
    ("gif", ['47', '49', '46', '38', '37', '61'], ['00', '3b']),
    ("gif", ['47', '49', '46', '38', '39', '61'], ['00', '3b']),
    ("docx",['50', '4b', '03', '04', '14', '00', '06', '00'],['50', '4b', '05', '06']),
    ("avi", ['41', '56', '49', '20', '4c', '49', '53', '54'], []),
    ("avi", ['52', '49', '46', '46'], []),
    ("png", ['89', '50', '4e', '47', '0d', '0a', '1a', '0a'], ['49', '45', '4e', '44', 'ae', '42', '60', '82']),
    ("pdf", ['25', '50', '44', '46'], ['25', '25', '45', '4f', '46']),
    ("bmp", ['42','4d'], []),

]

sig_heads = [
    ['ff', 'd8', 'ff', 'e0'],
    ['ff', 'd8', 'ff', 'e1'],
    ['ff', 'd8', 'ff', 'e8'],
    ['00', '00', '01', 'ba'], 
    ['25', '50', '44', '46'], 
    ['42', '4F', '4F', '4b', '4d', '4f', '42', '49'], 
    ['47', '49', '46', '38', '37', '61'],
    ['50', '4b', '03', '04', '14', '00', '06', '00'],
    ['41', '56', '49', '20', '4c', '49', '53', '54'],
    ['89', '50', '4e', '47', '0d', '0a', '1a', '0a']

]

sig_foots =  [
    ['ff', 'd9'],
    ['ff', 'd9'],
    ['ff', 'd9'],
    ['ff', 'd9'],
    ['ff', 'd9'],
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

data_section = hexdump_to_list(DISK, 448, 97661)
byte_data = data_section[1]
print(len(byte_data))
#print("checking: ", sig_heads[w])
i = 0
while i < len(byte_data) - 9:

    for w in range(len(sig_heads)):
        #print("agaisnt ", byte_data[i:i+len(sig_heads[w])])
        if file_signatures[w][1] == byte_data[i:i+len(file_signatures[w][1])]:
            print(f"found head {file_signatures[w]} at sector", i/512)

            j = i
            while j < len(byte_data) - 3:
                
                if file_signatures[w][2] == byte_data[j:j+len(file_signatures[w][2])]:
                    print(f"found footer {file_signatures[w]} at {j/512}")
                    break
                j = j + 1

            i = j

    i = i + 1

        