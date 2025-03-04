"""import struct

numbers = [2, 8, 14, 50, 102]

packed_data = bytearray()

for num in numbers:
    if isinstance(num, bool):
        packed_data.append(int(num))
    elif isinstance(num, int) and num >= -2147483648 and num <= 2147483647:
        packed_data.extend(struct.pack('i', num))  # int32
    elif isinstance(num, int) and num >= -9223372036854775808 and num <= 9223372036854775807:
        packed_data.extend(struct.pack('q', num))  # int64
    elif isinstance(num, float):
        packed_data.extend(struct.pack('f', num))  # float
    else:
        raise ValueError("Unsupported data type")
    
print(int(packed_data))"""

# indexes = [0, 2, 5, 7, 10, 50]
indexes = range(64)

# Combine the indexes using bitwise operations into a single int32 or int64
combined_integer = 0
for index in indexes:
    combined_integer |= (1 << index)

# Now 'combined_integer' contains the combined indexes

print(f"Encoded {indexes=} as {combined_integer=}")

decoded_indexes = []

# Extract the indexes using bitwise operations
index = 0
while combined_integer:
    if combined_integer & 1:
        decoded_indexes.append(index)
    combined_integer >>= 1
    index += 1

print(f"Decoded:\n{decoded_indexes=}\nfrom {combined_integer=}")

"""
Output:
Encoded indexes=range(0, 100) as combined_integer=1267650600228229401496703205375
Decoded:
decoded_indexes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
""" 