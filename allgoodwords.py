fn = 'allbadwords.txt'

with open(fn, 'r') as f:
    bad_words = [line.strip() for line in f]

# make a list of good_words from bad_words that consist only of lower case letters, no numbers or punctuation
good_words = [word.lower() for word in bad_words if len(word) >= 4 and word.isalpha()]

# write the good_words to a file
fn = 'allgoodwords.txt'
with open(fn, 'w') as f:
    for word in good_words:
        f.write(word + '\n')
