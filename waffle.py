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


# class of type Thread
class SolveThread(Thread):
    def __init__(self, input_grid, output_grid, max_depth=10):
        Thread.__init__(self)
        self.input_grid = input_grid
        self.output_grid = output_grid
        self.max_depth = max_depth
        self.result = None
    
    def run(self):
        self.result = find_path(self.input_grid, self.output_grid, self.max_depth)
        print ("I am done -- max_depth = %d and do I have a result? %s" % (self.max_depth, 'Yes' if self.result is not None else 'No'))


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
            threads = [SolveThread(normalize_grid(input_grid), normalize_grid(output_grid), i+10) for i in range(0, 5)]
            for thread in threads:
                thread.start()
            # sleep 1 while any threads are running
            while any([thread.is_alive() for thread in threads]):
                time.sleep(1)
            result_heap = []
            for thread in threads:
                if thread.result:
                    heapq.heappush(result_heap, thread.result)
            if result_heap:
                result = heapq.heappop(result_heap)
                print (result)

    # return the output grid
    return jsonify(output_grid)

def find_path(input_grid: list, output_grid: list, max_depth=10):
    "find the shortest path between two grids"

    start_time = time.time()

    heap = []

    heapq.heappush(heap, (calc_distance(input_grid, output_grid), input_grid, []))

    while True:
        distance, grid, path = heapq.heappop(heap)
        path_len = len(path)

        if distance < 1:
            if path_len <= max_depth:
                return (path_len, path)

        # if elapsed time is over five seconds, return None
        if time.time() - start_time > 20:
            return None

        if path_len >= max_depth:
            time.sleep(0)
            continue

        # make an array of indexes for positions where input_grid and output_grid differ
        unmatched = calc_unmatched(grid, output_grid)

        for swap in combinations(unmatched, 2):
            new_grid = swap_grid(grid, swap)
            dist = calc_distance(new_grid, output_grid)
            heapq.heappush(heap, (dist, new_grid, path + [swap]))


def calc_unmatched(input_grid, output_grid):
    "return the indices of the letters in the input grid that do not match the output grid"
    return [i for i in range(len(input_grid)) if input_grid[i] != output_grid[i]]


def swap_grid(grid, swap):
    "return a new grid with the letters at the given indexes swapped"
    new_grid = grid.copy()
    new_grid[swap[0]], new_grid[swap[1]] = new_grid[swap[1]], new_grid[swap[0]]
    return new_grid


def normalize_grid(input_grid: list) -> list:
    "flatten the letter grid into a list of letters"
    return [char[0] for row in input_grid for char in row]


def calc_distance(input: list, solution: list) -> int:
    """calculate the distance between two grids.  A letter in the same position is
worth 0 points.  A letter in the same word but a different position is worth
1 point.  A letter not in the word is worth 2 points."""
    distance = 0
    for x, dx in norm_dist:
        guess = [input[x+dx*i] for i in range(5)]
        word = [solution[x+dx*i] for i in range(5)]
        distance += process_norm_word(word, guess)
    return distance


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
