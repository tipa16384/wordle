from itertools import combinations
from collections import defaultdict

vowels = 'aeiouy'

word_file_name = '/usr/share/dict/linux.words'

# read a list of words from wordle.txt

def read_words():
    with open(word_file_name, 'r') as f:
        return [line.strip() for line in f]

def checker(word_list):
    for words in combinations(word_list, 2):
        cword = ''.join(words)
        # does cword contain all vowels?
        if all(vowel in cword for vowel in vowels):
            # does cword contain no repeated letters?
            if len(set(cword)) == len(cword):
                print (cword)
                yield cword

def get_letter_score(word_list: list) -> dict:
    """
    Get the letter score for each letter.
    """
    letter_score = defaultdict(int)
    for word in word_list:
        for letter in word:
            letter_score[letter] += 1
    return letter_score

def sort_words_by_score(word_list: list) -> list:
    """
    Sort the words by score.
    """
    letter_score = get_letter_score(word_list)
    return sorted(word_list, key=lambda word: sum(letter_score[letter] for letter in set(word)), reverse=True)


if __name__ == '__main__':
    print (f"Reading words from {word_file_name}")
    word_list = read_words()
    print (f"Found {len(word_list)} words")
    word_list = [word for word in word_list if len(word) == 6 and word.islower()]
    print (f"Found {len(word_list)} words of length 6")

    word_list = [c for c in checker(word_list)]
    word_list = sort_words_by_score(word_list)
    print (word_list[0])

