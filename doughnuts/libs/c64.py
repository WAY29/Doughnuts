
C64_TABLE = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
    'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', '?'
]

def encrypt(s: str):
    bits = "".join(bin(byte)[2:].zfill(8) for byte in bytes(s.encode('utf8')))[::-1]
    length = len(bits)
    for count in range(length - 1):
        bits = bits[:count] + str(int(bits[count]) ^
                                  int(bits[count+1])) + bits[count + 1:]
        for i in range(11):
            bits = (bits[-1]+bits[:-1])[::-1]
    left = ""
    right = ""
    for i in range(length):
        if(not i % 2):
            left += bits[i]
        else:
            right += bits[i]
    data = right[:len(right)//2] + "".join(str(int(byte1) ^ int(byte2)) for byte1, byte2 in zip(left, right)) + right[len(right)//2:]
    data = data + "".join(str(byte % 2) for byte in range(6-len(data) % 6))
    result = "".join(C64_TABLE[int(data[i*6:(i+1)*6], 2)] for i in range(len(data)//6))

    return result


def decrypt(s: str):

    data = "".join(bin(C64_TABLE.index(font))[2:].zfill(6) for font in s)
    data = data[:-(len(data) % 8)]
    data_len = len(data)
    right = data[:data_len//4] + data[-data_len//4:]
    left = "".join(str(int(byte1) ^ int(byte2)) for byte1, byte2 in zip(data[data_len//4:data_len//4*3], right))
    bits = ""

    for i in range(data_len):
        if(not i % 2):
            bits += left[i//2]
        else:
            bits += right[i//2]

    for count in range(data_len - 1, 0, -1):
        for i in range(11):
            bits = bits[::-1]
            bits = (bits[1:]+bits[0])
        bits = bits[:count - 1] + str(int(bits[count]) ^ int(bits[count - 1])) + bits[count:]
    bits = bits[::-1]
    result = "".join(chr(int(bits[x*8:(x+1)*8], 2)) for x in range(len(bits)//8)).encode("latin1").decode('utf8')

    return result
