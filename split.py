import sys

text = sys.stdin.readlines()[0][:-1]

data = text.split(', ')

total = len(data)

split_point = int(total / 4)

first_part = data[:split_point]

print(f'First: {len(first_part)}')

with open('unsuccessful_hard_first.txt', 'w') as file:
    file.writelines(','.join(first_part))

second_part = data[split_point:split_point*2]

print(f'Second: {len(second_part)}')

with open('unsuccessful_hard_second.txt', 'w') as file:
    file.writelines(','.join(second_part))

third_part = data[split_point*2:split_point*3]

print(f'Third: {len(third_part)}')

with open('unsuccessful_hard_third.txt', 'w') as file:
    file.writelines(','.join(third_part))

fourth_part = data[split_point*3:]

print(f'Fourth: {len(fourth_part)}')

with open('unsuccessful_hard_fourth.txt', 'w') as file:
    file.writelines(','.join(fourth_part))

assert total == len(first_part) + len(second_part) + len(third_part) + len(fourth_part)