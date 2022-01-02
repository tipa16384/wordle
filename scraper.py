import re

words = list()

with open('words.dat') as f:
    words += re.findall(r'\w+', f.read())

print (f"Length of words: {len(words)}")

# print first 20 words
print (f"First 20 words: {words[:20]}")

# write words to wordle.txt
with open('wordle.txt', 'w') as f:
    f.write('\n'.join(words))

