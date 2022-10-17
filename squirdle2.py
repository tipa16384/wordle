import pandas as pd
import random
import math

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

    return pokemon

def distance(pokemon, gen, height, weight):
    return math.sqrt((gen - pokemon.gen)**2 + (height - pokemon.height)**2 + (weight - pokemon.weight)**2)

if __name__ == '__main__':
    pokemon = parse_pokedex()
    # calculate average generation
    gen = math.floor(sum([p.gen for p in pokemon]) / len(pokemon))
    print ('Average generation is {}'.format(gen))
    # calculate average height
    height = sum([p.height for p in pokemon]) / len(pokemon)
    print ('Average height is {}'.format(height))
    # calculate average weight
    weight = sum([p.weight for p in pokemon]) / len(pokemon)
    print ('Average weight is {}'.format(weight))
    # most popular type1
    type1 = {}
    for p in pokemon:
        if p.type[0] not in type1:
            type1[p.type[0]] = 0
        type1[p.type[0]] += 1
    type1 = sorted(type1.items(), key=lambda x: x[1], reverse=True)
    print ('Most popular type1 is {}'.format(type1[0][0]))
    type2 = {}
    for p in pokemon:
        if len(p.type) > 1:
            if p.type[1] not in type2:
                type2[p.type[1]] = 0
            type2[p.type[1]] += 1
    type2 = sorted(type2.items(), key=lambda x: x[1], reverse=True)
    print ('Most popular type2 is {}'.format(type2[0][0]))

    # calculate pokemon with lowest distance
    closest = None
    closest_distance = None
    for p in pokemon:
        if len(p.type) > 1:
            continue
        if p.type[0] != type1[0][0]:
            continue
        if p.gen != gen:
            continue
        d = distance(p, gen, height, weight)
        if closest_distance is None or d < closest_distance:
            closest = p
            closest_distance = d
    print ('Closest pokemon is {}'.format(closest))


        
