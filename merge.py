import sys

args = sys.argv[1:]

games = []

total = 0

for arg in args:
    with open(arg, 'r') as file:
        data = file.read()[:-1].split(',')
        games.extend(data)
        total += len(data)
        print(f'{arg}: {len(data)}')

print(f'Total: {len(games)}')

assert total == len(games)

split_point = int(total / 3)

first_part = games[:split_point]

print(f'First: {len(first_part)}')

with open('unsuccessful_first.txt', 'w') as file:
    file.writelines(','.join(first_part))

second_part = games[split_point:split_point*2]

print(f'Second: {len(second_part)}')

with open('unsuccessful_second.txt', 'w') as file:
    file.writelines(','.join(second_part))

third_part = games[split_point*2:]

print(f'Third: {len(third_part)}')

with open('unsuccessful_third.txt', 'w') as file:
    file.writelines(','.join(third_part))

assert total == len(first_part) + len(second_part) + len(third_part)