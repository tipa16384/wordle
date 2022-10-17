import pandas as pd
import random

pokedex_fn = 'pokedex.html'

class Pokemon:
    def __init__(self, gen, number, name, type, height, weight):
        self.gen = gen
        self.number = number
        self.name = name
        self.type = type
        self.height = height
        self.weight = weight

    def __str__(self):
        return 'Pokemon: {} {} {} {} {} {}'.format(self.number, self.gen, self.name, self.type, self.height, self.weight)

class Rule:
    def __init__(self, guess_rule, trigger_rule, log_rule):
        self.guess_rule = guess_rule
        self.trigger_rule = trigger_rule
        self.log_rule = log_rule

    def apply(self, pokemon, guess, pool_map):
        pool = true_pool(pool_map)
        if self.guess_rule(guess, pokemon):
            trigger = False
            for px in pool:
                if self.trigger_rule(px, pokemon):
                    if not trigger:
                        print (self.log_rule(pokemon))
                        trigger = True
                    pool_map[px] = False

rule_list = [
    Rule(lambda guess, _: guess[0] == 'g', lambda px, p: px.gen != p.gen, lambda p: "!!!Removing gen different from {}".format(p.gen)),
    Rule(lambda guess, _: guess[0] == 'u', lambda px, p: px.gen <= p.gen, lambda p: "!!!Removing gen less than or equal to {}".format(p.gen)),
    Rule(lambda guess, _: guess[0] == 'd', lambda px, p: px.gen >= p.gen, lambda p: "!!!Removing gen greater than or equal to {}".format(p.gen)),
    Rule(lambda guess, p: guess[1:3] == 'yx' or (guess[1:3] == 'xx' and len(p.type) == 1), lambda px, _: len(px.type) == 1, lambda _: "!!!Removing pokemon with just one type"),
    Rule(lambda guess, _: guess[3] == 'g', lambda px, p: px.height != p.height, lambda p: "!!!Removing height different from {}".format(p.height)),
    Rule(lambda guess, _: guess[3] == 'u', lambda px, p: px.height <= p.height, lambda p: "!!!Removing height less than or equal to {}".format(p.height)),
    Rule(lambda guess, _: guess[3] == 'd', lambda px, p: px.height >= p.height, lambda p: "!!!Removing height greater than or equal to {}".format(p.height)),
    Rule(lambda guess, _: guess[4] == 'g', lambda px, p: px.weight != p.weight, lambda p: "!!!Removing weight different from {}".format(p.weight)),
    Rule(lambda guess, _: guess[4] == 'u', lambda px, p: px.weight <= p.weight, lambda p: "!!!Removing weight less than or equal to {}".format(p.weight)),
    Rule(lambda guess, _: guess[4] == 'd', lambda px, p: px.weight >= p.weight, lambda p: "!!!Removing weight greater than or equal to {}".format(p.weight))
]

def calc_gen(name, pokemon_number):
    if 'Hisuian ' in name:
        name = name[name.index('Hisuian '):]
        return 8, name
    if 'Galarian ' in name:
        name = name[name.index('Galarian '):]
        return 8, name
    if 'Alolan ' in name:
        name = name[name.index('Alolan '):]
        return 7, name
    if 'Mega ' in name:
        name = name[name.index('Mega '):]
        return 6, name
    if pokemon_number >= 1 and pokemon_number <= 151:
        return 1, name
    elif pokemon_number >= 152 and pokemon_number <= 251:
        return 2, name
    elif pokemon_number >= 252 and pokemon_number <= 386:
        return 3, name
    elif pokemon_number >= 387 and pokemon_number <= 493:
        return 4, name
    elif pokemon_number >= 494 and pokemon_number <= 649:
        return 5, name
    elif pokemon_number >= 650 and pokemon_number <= 721:
        return 6, name
    elif pokemon_number >= 722 and pokemon_number <= 809:
        return 7, name
    elif pokemon_number >= 810 and pokemon_number <= 905:
        return 8, name
    else:
        return 9, name

def parse_pokedex():
    tables = pd.read_html(pokedex_fn)
    raw_stats = tables[0].to_dict()
    names = raw_stats['Name']
    types = raw_stats['Type']
    heights = raw_stats['Height (m)']
    weights = raw_stats['Weight (kgs)']
    numbers = raw_stats['#']

    print ('There are {} pokemon in the pokedex'.format(len(names)))

    # Create a list of Pokemon objects
    pokemon = []
    for k, v in names.items():
        name = v
        type = types[k].strip().split(' ')
        height = float(heights[k])
        weight = float(weights[k])
        num_s = numbers[k]
        num = 0 if num_s == '???' else int(num_s)
        gen, name = calc_gen(name, num)
        # if gen between 1 and 8 inclusive
        if gen >= 1 and gen <= 8:
            pokemon.append(Pokemon(gen, num, name, type, height, weight))

    print (pokemon[0])

    return pokemon

def true_pool(pool):
    # return all pokemon in pool that are True
    return [p for p in pool if pool[p]]

if __name__ == '__main__':
    pokemon = parse_pokedex()
    # make a dictionary with key pokemon and value boolean True
    xpool = {p: True for p in pokemon}

    while True:
        pool = true_pool(xpool)
        # count the number of pokemon in the pool with value = True
        count = len(pool)
        
        if count == 0:
            print ('There are no pokemon left in the pool')
            break
        else:
            print ('There are {} pokemon in the pool'.format(count))

        # pick a random pokemon in the pool with value True
        p = random.choice(pool)

        # prompt with the name of the Pokemon
        print ('Try this pokemon: {}'.format(p.name))
        # get the user input
        while True:
            guess = input('Enter the response from Squirdle: ')
            # if guess is empty, exit the program with message "Goodbye"
            if guess == '':
                print ('Goodbye')
                exit(0)
            # if the user input is not five characters, or the characters are anything but u, d, x or g, raise an error
            if len(guess) == 5 and all(c in 'udxgy' for c in guess):
                break
            print ('Invalid response')
        for r in rule_list:
            r.apply(p, guess, xpool)
        types = guess[1:3]
        pool = true_pool(xpool)
        if len(p.type) == 1 and types[1] == 'g':
            trigger = False
            # set all pokemon with more than one type to False
            for px in pool:
                if len(px.type) > 1:
                    if not trigger:
                        print ("Removing pokemon with more than one type")
                        trigger = True
                    xpool[px] = False
            types = types[0] * 2
        pool = true_pool(xpool)
        # if types is 'xx', set all pokemon with either of the same types as the pokemon to False
        if types == 'xx':
            trigger = False
            for px in pool:
                # if any of p.type is in px.type, set xpool[px] to False
                if any(t in px.type for t in p.type):
                    if not trigger:
                        print ('Removing types: {}'.format(p.type))
                        trigger = True
                    xpool[px] = False
        # if types is 'gg', set all pokemon that don't have both of the same types as the pokemon to False
        elif types == 'gg' or types == 'yy':
            trigger = False
            for px in pool:
                # if any of p.type is not in px.type, set xpool[px] to False
                if not all(t in px.type for t in p.type):
                    if not trigger:
                        print ('Keeping types: {}'.format(p.type))
                        trigger = True
                    xpool[px] = False
        # if types is 'xg' or types is 'gx', set all pokemon that don't have either of the same types as the pokemon to False
        elif types == 'xg' or types == 'gx' or types == 'xy' or types == 'yx':
            trigger = False
            for px in pool:
                # if at least one of p.type isn't in px.type, set xpool[px] to False
                if not any(t in px.type for t in p.type):
                    if not trigger:
                        print ('One type is correct: {}'.format(p.type))
                        trigger = True
                    xpool[px] = False

    