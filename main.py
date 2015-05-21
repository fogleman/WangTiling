from collections import defaultdict
import cairo
import itertools
import operator
import os
import random

WIDTH = 16 * 2
HEIGHT = 9 * 2

WEIGHT_NONE = 10
WEIGHT_DEAD_END = 1
WEIGHT_TURN = 10
WEIGHT_STRAIGHT = 10
WEIGHT_T_JUNCTION = 10
WEIGHT_INTERSECTION = 10
WEIGHT_RIVER_TURN = 2
WEIGHT_RIVER_STRAIGHT = 2
WEIGHT_RIVER_BRIDGE = 2

if False:
    WEIGHT_NONE = random.randint(0, 10)
    WEIGHT_DEAD_END = random.randint(0, 10)
    WEIGHT_TURN = random.randint(0, 10)
    WEIGHT_STRAIGHT = random.randint(0, 10)
    WEIGHT_T_JUNCTION = random.randint(0, 10)
    WEIGHT_INTERSECTION = random.randint(0, 10)
    WEIGHT_RIVER_TURN = random.randint(0, 10)
    WEIGHT_RIVER_STRAIGHT = random.randint(0, 10)
    WEIGHT_RIVER_BRIDGE = random.randint(0, 10)

WEIGHTS = {
    '0000': WEIGHT_NONE,
    '0001': WEIGHT_DEAD_END,
    '0010': WEIGHT_DEAD_END,
    '0011': WEIGHT_TURN,
    '0100': WEIGHT_DEAD_END,
    '0101': WEIGHT_STRAIGHT,
    '0110': WEIGHT_TURN,
    '0111': WEIGHT_T_JUNCTION,
    '1000': WEIGHT_DEAD_END,
    '1001': WEIGHT_TURN,
    '1010': WEIGHT_STRAIGHT,
    '1011': WEIGHT_T_JUNCTION,
    '1100': WEIGHT_TURN,
    '1101': WEIGHT_T_JUNCTION,
    '1110': WEIGHT_T_JUNCTION,
    '1111': WEIGHT_INTERSECTION,
    '0022': WEIGHT_RIVER_TURN,
    '0202': WEIGHT_RIVER_STRAIGHT,
    '0220': WEIGHT_RIVER_TURN,
    '1212': WEIGHT_RIVER_BRIDGE,
    '2002': WEIGHT_RIVER_TURN,
    '2020': WEIGHT_RIVER_STRAIGHT,
    '2121': WEIGHT_RIVER_BRIDGE,
    '2200': WEIGHT_RIVER_TURN,
}

for k in itertools.product('012', repeat=4):
    k = ''.join(k)
    if k not in WEIGHTS:
        WEIGHTS[k] = 1

def load_tiles(path):
    result = defaultdict(list)
    for name in os.listdir(path):
        key = name[:4]
        if key not in WEIGHTS:
            continue
        surface = cairo.ImageSurface.create_from_png(os.path.join(path, name))
        result[key].append(surface)
    return result

def generate(tiles, width, height):
    tile_size = tiles.values()[0][0].get_width()
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24, width * tile_size, height * tile_size)
    dc = cairo.Context(surface)
    defaults = []
    for k, weight in WEIGHTS.items():
        if k not in tiles:
            continue
        defaults.extend([k] * weight)
    digits = sorted(set(reduce(operator.add, WEIGHTS)))
    lookup = {}
    for y in range(height):
        for x in range(width):
            n = lookup.get((x, y - 1), random.choice(defaults))[2]
            w = lookup.get((x - 1, y), random.choice(defaults))[1]
            choices = []
            for e in digits:
                for s in digits:
                    k = n + e + s + w
                    if k not in tiles:
                        continue
                    choices.extend([k] * WEIGHTS.get(k))
            k = random.choice(choices)
            lookup[(x, y)] = k
            tile = random.choice(tiles[k])
            dc.set_source_surface(tile, x * tile_size, y * tile_size)
            dc.paint()
    return surface

def main():
    tiles = load_tiles('tiles1')
    surface = generate(tiles, WIDTH, HEIGHT)
    surface.write_to_png('output.png')

if __name__ == '__main__':
    main()
