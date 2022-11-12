
def process_word(word: str, guess: str, result: str) -> bool:
    "return True if the word matches the guess and result"
    nresult = ['b'] * len(result)
    # make a dict ith key letter and value count for word
    word_dict = {}
    for letter in word:
        if letter in word_dict:
            word_dict[letter] += 1
        else:
            word_dict[letter] = 1

    # put a 'G' in nresult for each letter in word that matches the corresponding letter in guess
    for i in range(len(word)):
        if word[i] == guess[i]:
            nresult[i] = 'g'
            word_dict[guess[i]] -= 1

    for i in range(len(word)):
        if nresult[i] == 'g':
            continue
        if guess[i] in word_dict and word_dict[guess[i]] > 0:
            nresult[i] = 'y'
            word_dict[guess[i]] -= 1

    nresult = ''.join(nresult)

    return nresult == result
