import cairo
import operator
import random

TILE_SIZE = 64
WIDTH = 16 * 2
HEIGHT = 9 * 2
WEIGHT_BASE = 2
RANDOM_WEIGHTS = False

WEIGHT_NONE = 4
WEIGHT_DEAD_END = 0
WEIGHT_TURN = 2
WEIGHT_STRAIGHT = 3
WEIGHT_T_JUNCTION = 1
WEIGHT_INTERSECTION = 1
WEIGHT_RIVER_TURN = 2
WEIGHT_RIVER_STRAIGHT = 2
WEIGHT_RIVER_BRIDGE = 1

if RANDOM_WEIGHTS:
    WEIGHT_NONE = random.randint(0, 5)
    WEIGHT_DEAD_END = random.randint(0, 5)
    WEIGHT_TURN = random.randint(0, 5)
    WEIGHT_STRAIGHT = random.randint(0, 5)
    WEIGHT_T_JUNCTION = random.randint(0, 5)
    WEIGHT_INTERSECTION = random.randint(0, 5)
    WEIGHT_RIVER_TURN = random.randint(0, 5)
    WEIGHT_RIVER_STRAIGHT = random.randint(0, 5)
    WEIGHT_RIVER_BRIDGE = random.randint(0, 5)

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

def load_tiles():
    result = {}
    for key in WEIGHTS:
        path = 'tiles/%s.png' % key
        surface = cairo.ImageSurface.create_from_png(path)
        result[key] = surface
    return result

def rank(n):
    if not n:
        return 0
    return WEIGHT_BASE ** (n - 1)

def generate(tiles, width, height):
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24, width * TILE_SIZE, height * TILE_SIZE)
    dc = cairo.Context(surface)
    defaults = []
    for k, weight in WEIGHTS.items():
        defaults.extend([k] * rank(weight))
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
                    choices.extend([k] * rank(WEIGHTS.get(k)))
            k = random.choice(choices)
            lookup[(x, y)] = k
            dc.set_source_surface(tiles[k], x * TILE_SIZE, y * TILE_SIZE)
            dc.paint()
    return surface

def main():
    tiles = load_tiles()
    surface = generate(tiles, WIDTH, HEIGHT)
    surface.write_to_png('output.png')

if __name__ == '__main__':
    main()