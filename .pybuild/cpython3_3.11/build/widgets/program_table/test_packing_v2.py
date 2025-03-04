numbers = [2, 8, 14, 50, 102]

# Calculate the sum of the numbers
total = sum(numbers)

decoded_numbers = [total]  # Start with the total sum

# Calculate the original numbers by subtracting from the sum
for i in range(len(numbers) - 1, 0, -1):
    decoded_numbers.insert(0, decoded_numbers[0] - numbers[i])

print(numbers)
print(f"{total=}")
print(f"{decoded_numbers=}")

