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

    def get_stats(self):
        pass

    def __str__(self):
        return 'Pokemon: {} {} {} {} {} {}'.format(self.number, self.gen, self.name, self.type, self.height, self.weight)

def calc_gen(name, pokemon_number):
    if 'Hisuian ' in name or 'Galarian ' in name:
        return 8
    if 'Alolan ' in name:
        return 7
    if 'Mega ' in name:
        return 6
    if pokemon_number >= 1 and pokemon_number <= 151:
        return 1
    elif pokemon_number >= 152 and pokemon_number <= 251:
        return 2
    elif pokemon_number >= 252 and pokemon_number <= 386:
        return 3
    elif pokemon_number >= 387 and pokemon_number <= 493:
        return 4
    elif pokemon_number >= 494 and pokemon_number <= 649:
        return 5
    elif pokemon_number >= 650 and pokemon_number <= 721:
        return 6
    elif pokemon_number >= 722 and pokemon_number <= 809:
        return 7
    elif pokemon_number >= 810 and pokemon_number <= 905:
        return 8
    else:
        return 9

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
        type = types[k].strip().split(' ')
        height = float(heights[k])
        weight = float(weights[k])
        num_s = numbers[k]
        if num_s == '???':
            num = 0
        else:
            num = int(num_s)
        gen = calc_gen(v, num)
        if gen < 1 or gen > 8:
            continue
        pokemon.append(Pokemon(gen, num, v, type, height, weight))

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
        # if guess[0] is 'g', set all the pokemon in the pool with a different generation than the pokemon to False
        if guess[0] == 'g':
            trigger = False
            for px in pool:
                if px.gen != p.gen:
                    if not trigger:
                        print ("Removing gen different from {}".format(p.gen))
                        trigger = True
                    xpool[px] = False
        # if guess[0] is 'u', set all the pokemon with a generation less than or equal to the pokemon to False
        elif guess[0] == 'u':
            trigger = False
            for px in pool:
                if px.gen <= p.gen:
                    if not trigger:
                        print ("Removing gen less than or equal to {}".format(p.gen))
                        trigger = True
                    xpool[px] = False
        # if guess[0] is 'd', set all the pokemon with a generation greater than or equal to the pokemon to False
        elif guess[0] == 'd':
            trigger = False
            for px in pool:
                if px.gen >= p.gen:
                    if not trigger:
                        print ("Removing gen greater than or equal to {}".format(p.gen))
                        trigger = True
                    xpool[px] = False
        types = guess[1:3]
        pool = true_pool(xpool)
        if types == 'yx' or (types == 'xx' and len(p.type) == 1):
            trigger = False
            # remove all pokemon with just one type
            for px in pool:
                if len(px.type) == 1:
                    if not trigger:
                        print ("Removing pokemon with just one type")
                        trigger = True
                    xpool[px] = False
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
        # if guess[3] is 'g', set all pokemon in the pool with a height different from p to False
        pool = true_pool(xpool)
        if guess[3] == 'g':
            trigger = False
            for px in pool:
                if p.height != px.height:
                    if not trigger:
                        print ('Removing height different from {}'.format(p.height))
                        trigger = True
                    xpool[px] = False
        # if guess[3] is 'u', set all pokemon in the pool with a height less than or equal to p to False
        elif guess[3] == 'u':
            trigger = False
            for px in pool:
                if px.height <= p.height:
                    if not trigger:
                        print ('Removing height less than or equal to {}'.format(p.height))
                        trigger = True
                    xpool[px] = False
        # if guess[3] is 'd', set all pokemon in the pool with a height greater than or equal to p to False
        elif guess[3] == 'd':
            trigger = False
            for px in pool:
                if px.height >= p.height:
                    if not trigger:
                        print ('Removing height greater than or equal to {}'.format(p.height))
                        trigger = True
                    xpool[px] = False
        # if guess[4] is 'g', set all pokemon in the pool with a weight different from p to False
        pool = true_pool(xpool)
        if guess[4] == 'g':
            trigger = False
            for px in pool:
                if px.weight != p.weight:
                    if not trigger:
                        print ('Removing weight different from {}'.format(p.weight))
                        trigger = True
                    xpool[px] = False
        # if guess[4] is 'u', set all pokemon in the pool with a weight less than or equal to p to False
        elif guess[4] == 'u':
            trigger = False
            for px in pool:
                if px.weight <= p.weight:
                    if not trigger:
                        print ('Removing weight less than or equal to {}'.format(p.weight))
                        trigger = True
                    xpool[px] = False
        # if guess[4] is 'd', set all pokemon in the pool with a weight greater than or equal to p to False
        elif guess[4] == 'd':
            trigger = False
            for px in pool:
                if px.weight >= p.weight:
                    if not trigger:
                        print ('Removing weight greater than or equal to {}'.format(p.weight))
                        trigger = True
                    xpool[px] = False

    