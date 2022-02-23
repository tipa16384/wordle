import re

symbols = '=0123456789+-*/'
num_syms = len(symbols)
num_positions = 8

guess = [0] * num_positions

pat = re.compile(r'^\d+([-+*/]\d+)*\=\d+$')
pat_zero = re.compile(r'(^0+\d|\D0+\d)')

def has_leading_zeros(s):
    return s[0] == '0'

print (f"Number of guesses: {num_syms ** num_positions}")

with open('equations.txt', 'w') as f:
    for i in range(num_syms ** num_positions):
        if not (i % 1000000):
            print (f"{i} combinations checked")
        val = i
        for j in range(num_positions):
            guess[j] = symbols[val % num_syms]
            val //= num_syms
        equ = ''.join(guess)
        if re.match(pat, equ) and not re.search(pat_zero, equ):
            zequ = equ.replace('=', '==')
            try:
                if eval(zequ):
                    f.write(equ + '\n')
            except:
                pass
