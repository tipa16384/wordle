from itertools import permutations

operations = [ '+', '-', '*', '/' ]

for ops in permutations(operations, 3):
    equation = '8 {} 2 {} 6 {} 2'.format(*ops)
    if eval(equation) == 16:
        print(equation, '= 16')
        break
