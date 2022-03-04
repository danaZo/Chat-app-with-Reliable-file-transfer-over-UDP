"""
Error
A condition when the receiver’s information does not match with the sender’s information.
That means a 0 bit may change to 1 or a 1 bit may change to 0.
Error-detecting code: additional data added to a given digital message to help us detect if any error has occurred
during transmission of the message.
We use Cyclic redundancy check (CRC).
CRC is based on binary division.
It uses Generator Polynomial which is available on both sender and receiver sides.
"""

# receiving string with bytes
# packet max size is 1350 bytes

# CRC KEY: 1001
# Code: CRC key length -1 -> 000 appended at end of data.
# Key:1001
# key is known to both the side sender and receiver

# SENDER SIDE:
# The sender sends the input_string
# first step: this string is converted to binary string
# second step: this data is encoded using the CRC code using the key on the sender side.
# third step: this encoded data is sent to the receiver.
# last step: Receiver decodes the encoded data string to verify whether there was any error or not.

"""
xor function:
a and b are byte strings, a is the string data we check, 
b is the CRC generator.
from the left side, we check each byte if it's the same at both strings,
if it is - the result occurs to be '0'. otherwise: '1'.
example:
a = 1010000000
b = 1001
xor(a,b) = 0011000000
"""

def xor(a, b):
    result = []

    # Traverse all bits, if bits are same, then XOR is 0, else 1
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')

    return ''.join(result)


# Performs Modulo-2 division
def mod2div(dividend, divisor):
    # Number of bits to be XORed at a time.
    pick = len(divisor)

    # Slicing the dividend to appropriate length for particular step
    tmp = dividend[0: pick]

    while pick < len(dividend):

        if tmp[0] == '1':

            # replace the dividend by the result of XOR and pull 1 bit down
            tmp = xor(divisor, tmp) + dividend[pick]

        else:  # If leftmost bit is '0'

            # If the leftmost bit of the dividend (or the part used in each step) is 0, the step cannot
            # use the regular divisor; we need to use an all-0s divisor.
            tmp = xor('0' * pick, tmp) + dividend[pick]

        # increment pick to move further
        pick += 1

    # For the last n bits, we have to carry it out normally as increased value of pick will cause Index Out of Bounds.
    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0' * pick, tmp)

    checkword = tmp
    return checkword


"""
function encodeData:
Used at the sender side to encode data by appending remainder of modular division at the end of data.
"""

def encodeData(data, key):
    l_key = len(key)

    # Appends n-1 zeroes at end of data
    appended_data = data + '0' * (l_key - 1)
    remainder = mod2div(appended_data, key)

    # Append remainder in the original data
    codeword = data + remainder
    return codeword


