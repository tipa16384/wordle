# import flask and jsonify
from flask import Flask, jsonify, request
from itertools import combinations
import heapq
from threading import Thread, active_count
import time

solve_directions = [(0, 0, 0, 1), (0, 2, 1, 0), (4, 0, 0, 1),
                    (0, 0, 1, 0), (0, 4, 1, 0), (2, 0, 0, 1)]

norm_dist = [(0, 1), (0, 5), (2, 5), (4, 5), (10, 1), (20, 1)]

# read a list of words from wordle.txt
with open('all.txt') as f:
    wordle_words = f.read().splitlines()

# all words in wordle_words to upper case
wordle_words = [word.upper() for word in wordle_words]

# start an http server to listen for requests on the /terrachat endpoint
app = Flask(__name__)

# add a flask endpoint that returns the file index.html when the user visits the root url
@app.route('/')
def index():
    "return the waffle.html file"
    return app.send_static_file('waffle.html')

# Flask endpoint that takes a grid of 25 characters and returns a grid of 25 characters
# that is the same as the input grid but with the letters in the grid replaced with
# the letters that are in the same row or column as the input letter.
# endpoint: /waffle
# input: 5x5 grid of characters
# output: 5x5 grid of characters
# allow cross origin requests

@app.route('/waffle', methods=['POST'])
def waffle():
    # get the input grid
    input_grid = request.get_json()
    print_grid("input", input_grid)

    letters_in_grid = set([char[0] for row in input_grid for char in row])
    possibility_dictionary = make_possibility_dictionary(
        input_grid, letters_in_grid)

    potential_solutions = []

    solve(input_grid, letters_in_grid, possibility_dictionary,
          solve_directions, potential_solutions)

    prime_letter_counts = make_letter_count_map(input_grid)

    # if prime_letter_counts == 0, return a 500 error.
    if not potential_solutions:
        return jsonify({'error': 'No solutions found'}), 500

    letter_counts = make_letter_count_map(potential_solutions[0])

    for solution in potential_solutions:
        letter_counts = make_letter_count_map(solution)
        if letter_counts == prime_letter_counts:
            output_grid = solution
            print_grid("solution", solution)
            new_solution(normalize_grid(input_grid), normalize_grid(solution))

    # return the output grid
    return jsonify(output_grid)

def new_solution(current: list, goal: list, current_path = []) -> bool:
    if len(current_path) > 10:
        return False
    
    #print (f"{current}\n{goal}\n{current_path}\n")
    if current == goal:
        print_path (current_path)
        return True
    
    # make a list of letters that don't match the goal
    unmatched = [current[i] for i in range(len(current)) if current[i] != goal[i]]
    # make a list of letters that are only once in the unmatched list
    unique = [letter for letter in unmatched if unmatched.count(letter) == 1]
    if not unique:
        unique = unmatched
    # for each letter in "unique", make a new_current with the letter swapped with the letter at
    # its destination in the goal, add the letter to the path, and call new_solution with the new_current
    for letter in unique:
        # unsolved grid has spaces where goal and current are the same
        unsolved = [' ' if current[i] == goal[i] else current[i] for i in range(len(current))]
        unsolved_goal = [' ' if current[i] == goal[i] else goal[i] for i in range(len(current))]

        #print (f"{list_to_string(unsolved)}\n{list_to_string(unsolved_goal)}\n")

        # find all the indexes of the letter in the unsolved grid
        indexes = [i for i in range(len(unsolved)) if unsolved[i] == letter]
        for index in indexes:
            # final all the indexes of the letter in the goal grid
            goal_indexes = [i for i in range(len(unsolved_goal)) if unsolved_goal[i] == letter]
            for goal_index in goal_indexes:
                new_current = [current[i] for i in range(len(current))]
                goal_letter = unsolved[goal_index]
                # swap the letter in the unsolved grid with the letter in the goal grid
                new_current[index], new_current[goal_index] = new_current[goal_index], new_current[index]
                if new_solution(new_current, goal, current_path + [(letter, index, goal_letter, goal_index)]):
                    return True
    
    return False

print_template = '...... . ....... . ......'

def print_path(path: list):
    "print the path"

    for row in range(5):
        out_s = ''
        for letter, index, goal_letter, goal_index in path:
            ri = row * 5
            rj = (row + 1) * 5
            slice = print_template[ri:rj]
            if index >= ri and index < rj:
                slice = slice[:index - ri] + letter + slice[index - ri + 1:]
            if goal_index >= ri and goal_index < rj:
                slice = slice[:goal_index - ri] + goal_letter + slice[goal_index - ri + 1:]
            out_s += f' {slice} '
        print(out_s)
    print()

def list_to_string(input_list: list) -> str:
    "convert a list of letters to a string"
    return ''.join(input_list)

def normalize_grid(input_grid: list) -> list:
    "flatten the letter grid into a list of letters"
    return [char[0] for row in input_grid for char in row]


def make_letter_count_map(input_grid: list) -> dict:
    "make a dictionary of letters and their counts in the grid"
    letter_count_map = {}
    for row in input_grid:
        for char in row:
            if len(char) == 2:
                if char[0] in letter_count_map:
                    letter_count_map[char[0]] += 1
                else:
                    letter_count_map[char[0]] = 1
    return letter_count_map


def solve(input_grid, letters_in_grid, possibility_dictionary, solve_directions, potential_solutions):
    "solve the waffle puzzle"
    if not solve_directions:
        potential_solutions.append(input_grid)
        return
    dir = solve_directions[0]
    possible_words = possibility_dictionary[dir]
    if not possible_words:
        return
    x, y, dx, dy = dir
    for word in possible_words:
        # new_grid is a copy of input_grid
        new_grid = [row[:] for row in input_grid]
        for i in range(5):
            c = new_grid[y + i * dy][x + i * dx][0]
            f = new_grid[y + i * dy][x + i * dx][1]
            w = word[i]
            if f == 'G' and c != w:
                break
            new_grid[y + i * dy][x + i * dx] = w + 'G'
        else:
            solve(new_grid, letters_in_grid, possibility_dictionary,
                  solve_directions[1:], potential_solutions)


def print_grid(label, input_grid):
    "print the grid with the given label"
    print(label)
    for row in input_grid:
        print(''.join([char[0] if len(char) == 2 else ' ' for char in row]))
    print()


def make_possibility_dictionary(input_grid, letters_in_grid):
    "make a dictionary of possible words for each direction"
    dir_word_list = {}
    for dir in solve_directions:
        possible_set = find_possible_words_by_dir(
            input_grid, letters_in_grid, dir)
        dir_word_list[dir] = possible_set
    return dir_word_list


def find_possible_words_by_dir(input_grid, letters_in_grid, dir):
    "find the possible words for the given direction"
    word, flags = extract_word(input_grid, dir)
    possible_words = find_possible_words(word, flags, letters_in_grid)
    if flags[0] == 'L':
        xflags = 'N' + flags[1:]
        possible_words += find_possible_words(word, xflags, letters_in_grid)
    if flags[4] == 'L':
        xflags = flags[:4] + 'N'
        possible_words += find_possible_words(word, xflags, letters_in_grid)
    if flags[2] == 'L':
        xflags = flags[:2] + 'N' + flags[3:]
        possible_words += find_possible_words(word, xflags, letters_in_grid)
    if flags[0] == 'L' and flags[4] == 'L':
        xflags = 'N' + flags[1:4] + 'N'
        possible_words += find_possible_words(word, xflags, letters_in_grid)
    return set(possible_words)


def find_possible_words(guess, flags, letters_in_grid):
    "find the possible words for the given guess and flags"
    word_list = []
    for word in wordle_words:
        # if word has a letter not in letters_in_grid then skip it
        if not set(word).issubset(letters_in_grid):
            continue
        if process_word(word, guess, flags):
            word_list.append(word)
    return word_list


def process_word(word: str, guess: str, result: str) -> bool:
    "return True if the word matches the guess and result"
    nresult = ['N'] * len(result)
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
            nresult[i] = 'G'
            word_dict[guess[i]] -= 1

    for i in range(len(word)):
        if nresult[i] == 'G':
            continue
        if guess[i] in word_dict and word_dict[guess[i]] > 0:
            nresult[i] = 'L'
            word_dict[guess[i]] -= 1

    nresult = ''.join(nresult)

    return nresult == result


def process_norm_word(word: list, guess: list) -> int:
    "return the distance between the word and guess"
    nresult = [2] * len(word)
    # make a dict with key letter and value count for word
    word_dict = {}
    for letter in word:
        if letter in word_dict:
            word_dict[letter] += 1
        else:
            word_dict[letter] = 1

    # put a 0 in nresult for each letter in word that matches the corresponding letter in guess
    for i in range(len(word)):
        if word[i] == guess[i]:
            nresult[i] = 0
            word_dict[guess[i]] -= 1

    # for i in range(len(word)):
    #     if nresult[i] == 0:
    #         continue
    #     if guess[i] in word_dict and word_dict[guess[i]] > 0:
    #         nresult[i] = 1
    #         word_dict[guess[i]] -= 1

    return sum(nresult)


def extract_word(input_grid, dir):
    "extract the word and flags from the input grid for the given direction"
    x, y, dx, dy = dir
    word = ''.join([input_grid[y + i * dy][x + i * dx][0] for i in range(5)])
    flags = ''.join([input_grid[y + i * dy][x + i * dx][1] for i in range(5)])
    return word, flags


# if main module
if __name__ == '__main__':
    app.run()
