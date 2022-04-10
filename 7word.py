import sys
from collections import defaultdict

word_file_name = '/usr/share/dict/linux.words'
deutsch = False

english_phrases = [
    "Read %d words from %s",
    "No words left to guess",
    "Only one word left to guess: %s",
    "There are %d words left to guess",
    "Words: %s",
    "Exiting"
]

deutsch_phrases = [
    "Ich habe %d Wörter aus %s gelesen",
    "Es gibt keine Wörter mehr zu erraten",
    "Nur noch ein Wort zu erraten: %s",
    "Es gibt %d Wörter zu erraten",
    "Wörter: %s",
    "Verlassen"
]

def get_phrase(index: int) -> str:
    if deutsch:
        return deutsch_phrases[index]
    else:
        return english_phrases[index]

def okay_word(word: str) -> bool:
    """
    Word is all lower case and exactly six characters long.
    """
    return word.islower() and len(word) == 7

def read_word_map():
    """
    Read the word map from the wordle file.
    """
    global deutsch, word_file_name
    word_map = {}
    with open(word_file_name, 'r') as f:
        for line in f:
            word = line.strip()
            if okay_word(word):
                word_map[word] = True
    if word_file_name[0] == 'd':
        deutsch = True
    print (get_phrase(0) % (len(word_map), word_file_name))
    return word_map

def get_letter_score(word_list: list) -> dict:
    """
    Get the letter score for each letter.
    """
    letter_score = defaultdict(int)
    for word in word_list:
        for letter in word:
            letter_score[letter] += 1
    return letter_score

def sort_words_by_score(word_map: dict) -> list:
    """
    Sort the words by score.
    """
    valid_word_list = list(word for word in word_map if word_map[word])
    letter_score = get_letter_score(valid_word_list)
    return sorted(valid_word_list, key=lambda word: sum(letter_score[letter] for letter in set(word)), reverse=True)

def process_word(word: str, guess: str, result: str) -> bool:
    nw, ng, nr = '', '', ''
    # look for direct matches
    for i in range(len(word)):
        w = word[i]
        g = guess[i]
        r = result[i]
        if r == 'g':
            if w != g:
                return False
        else:
            nw += w
            ng += g
            nr += r
    # if we used all the letters, return true
    if not nw: return True
    # look for matches in the rest of the word
    for i in range(len(nw)):
        w = nw[i]
        g = ng[i]
        r = nr[i]
        if r == 'y' and (w == g or g not in nw):
            return False
        if r == 'b' and g in nw:
            return False
    return True

def make_guess(word_map: dict) -> bool:
    word_list = sort_words_by_score(word_map)
    
    if not word_list:
        print (get_phrase(1))
        return False
    
    num_words = len(word_list)
    if num_words == 1:
        print (get_phrase(2) % word_list[0])
    else:
        print (get_phrase(3) % num_words)
        if num_words <= 10:
            print (get_phrase(4) % ', '.join(word_list))
        
    guess = word_list[0]
    
    valid_result = False
    while not valid_result:
        # input result with guess as prompt
        result = input(f"{guess}? ")
        if not result or result == 'g'*len(guess):
            print (get_phrase(5))
            return False
        valid_result = len(result) == len(guess) and all(c in 'gby' for c in result)
        if len(result) == len(guess) and not all(c in 'gby' for c in result):
            guess = result

    for word in word_list:
        word_map[word] = process_word(word, guess, result)

    return True
    

# if run from the command line, read the word_file_name from the command line
if __name__ == '__main__':
    if len(sys.argv) > 1:
        word_file_name = sys.argv[1]
    word_map = read_word_map()
    sorted_words = sort_words_by_score(word_map)
    assert process_word('torus', 'irate', 'bybyb')
    assert not process_word('frack', 'irate', 'bybyb')
    assert process_word('robot', 'rotor', 'ggygb')

    running = True
    while running:
        running = make_guess(word_map)


    
