# import flask and jsonify
from flask import Flask, jsonify, request
from itertools import combinations
import heapq
from functools import lru_cache

solve_directions = [(0, 0, 0, 1), (0, 2, 1, 0), (4, 0, 0, 1), (0, 0, 1, 0), (0, 4, 1, 0), (2, 0, 0, 1)]

# read a list of words from wordle.txt
with open('all.txt') as f:
    wordle_words = f.read().splitlines()

# all words in wordle_words to upper case
wordle_words = [word.upper() for word in wordle_words]

potential_solutions = []


# start an http server to listen for requests on the /terrachat endpoint
app = Flask(__name__)


# add a flask endpoint that returns the file index.html when the user visits the root url
@app.route('/')
def index():
#    print ('hit the root')
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
    global potential_solutions
    potential_solutions = []

    # get the input grid
    input_grid = request.get_json()
    print_grid ("input", input_grid)

    letters_in_grid = set([char[0] for row in input_grid for char in row])
    possibility_dictionary = make_possibility_dictionary(input_grid, letters_in_grid)
    # print (possibility_dictionary)

    solve(input_grid, letters_in_grid, possibility_dictionary, solve_directions)

    # print ('{} potential solutions'.format(len(potential_solutions)))
    
    prime_letter_counts = make_letter_count_map(input_grid)
    # print (prime_letter_counts)

    # if prime_letter_counts == 0, return a 500 error.
    if not potential_solutions:
        return jsonify({'error': 'No solutions found'}), 500

    # print_grid(potential_solutions[0])
    letter_counts = make_letter_count_map(potential_solutions[0])
    # print (letter_counts)

    for solution in potential_solutions:
        letter_counts = make_letter_count_map(solution)
        if letter_counts == prime_letter_counts:
            output_grid = solution
            print_grid("solution", solution)
            find_path(normalize_grid(input_grid), normalize_grid(solution))

    # return the output grid
    return jsonify(output_grid)

# use A* to find the shortest path between two grids
def find_path(input_grid: list, output_grid: list):
    heap = []

    print ('input grid: {}'.format(input_grid))
    print ('distance: {}'.format(calc_distance(input_grid, output_grid)))
    heapq.heappush(heap, (calc_distance(input_grid, output_grid), ''.join(input_grid), []))

    while True:
        distance, grid, path = heapq.heappop(heap)
        if distance < 1:
            print (distance, len(path), path)
            if len(path) <= 10:
                return

        if len(heap) > 1000000:
            return

        # if len(heap) % 1000 == 0:
        #     print ("heap: {} seen: {} hit: {}".format(len(heap), len(seen), hit))

        if len(path) >= 10:
            continue

        # grid is array of letters in grid
        grid = list(grid)

        # make an array of indexes for positions where input_grid and output_grid differ
        unmatched = calc_unmatched(grid, output_grid)

        for swap in combinations(unmatched, 2):
            new_grid = swap_grid(grid, swap)
            dist = calc_distance(new_grid, output_grid)
            heapq.heappush(heap, (dist, ''.join(new_grid), path + [swap]))

def calc_unmatched(input_grid, output_grid):
    return [i for i in range(len(input_grid)) if input_grid[i] != output_grid[i]]

def swap_grid(grid, swap):
    new_grid = grid.copy()
    new_grid[swap[0]], new_grid[swap[1]] = new_grid[swap[1]], new_grid[swap[0]]
    return new_grid

# concatenate the first letters in each cell of the grid
# to form a string
def normalize_grid(input_grid: list) -> list:
    return [char[0] for row in input_grid for char in row]

norm_dist = [
    (0,1), (0,5), (2,5), (4,5), (10, 1), (20,1)
]

# calculate the distance between two grids
def calc_distance(input: list, solution: list) -> int:
    distance = 0
    for x, dx in norm_dist:
        guess = [input[x+dx*i] for i in range(5)]
        word = [solution[x+dx*i] for i in range(5)]
        distance += process_norm_word(word, guess)
    return distance

# make a dictionary of letters and their counts in the grid
def make_letter_count_map(input_grid):
    letter_count_map = {}
    for row in input_grid:
        for char in row:
            if len(char) == 2:
                if char[0] in letter_count_map:
                    letter_count_map[char[0]] += 1
                else:
                    letter_count_map[char[0]] = 1
    return letter_count_map

def solve(input_grid, letters_in_grid, possibility_dictionary, solve_directions):
    global potential_solutions
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
            # print (dir, word)
            solve(new_grid, letters_in_grid, possibility_dictionary, solve_directions[1:])

def print_grid(label, input_grid):
    print (label)
    for row in input_grid:
        print(''.join([char[0] if len(char) == 2 else ' ' for char in row]))
    print()

def make_possibility_dictionary(input_grid, letters_in_grid):
    dir_word_list = { }
    for dir in solve_directions:
        possible_set = find_possible_words_by_dir(input_grid, letters_in_grid, dir)
        dir_word_list[dir] = possible_set
    return dir_word_list

def find_possible_words_by_dir(input_grid, letters_in_grid, dir):
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
    word_list = []
    for word in wordle_words:
        # if word has a letter not in letters_in_grid then skip it
        if not set(word).issubset(letters_in_grid):
            continue
        if process_word(word, guess, flags):
            word_list.append(word)
    return word_list

def process_word(word: str, guess: str, result: str) -> bool:
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
    # print (word, guess, result, nresult)
    return nresult == result

def process_norm_word(word: list, guess: list) -> int:
    nresult = [2] * len(word)
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
            nresult[i] = 0
            word_dict[guess[i]] -= 1

    for i in range(len(word)):
        if nresult[i] == 0:
            continue
        if guess[i] in word_dict and word_dict[guess[i]] > 0:
            nresult[i] = 1
            word_dict[guess[i]] -= 1

    # print (word, guess, result, nresult)
    return sum(nresult)

def extract_word(input_grid, dir):
    x, y, dx, dy = dir
    word = ''.join([input_grid[y + i * dy][x + i * dx][0] for i in range(5)])
    flags = ''.join([input_grid[y + i * dy][x + i * dx][1] for i in range(5)])
    return word, flags


# if main module
if __name__ == '__main__':
    app.run()
