from collections import defaultdict
import anneal
import cairo
import operator
import os
import random

TILE_SIZE = 64
WIDTH = 16 * 2
HEIGHT = 9 * 2

N = 1
E = 2
S = 3
W = 4

def pixel_distance(p1, p2):
    r1, g1, b1, a1 = p1
    r2, g2, b2, a2 = p2
    r, g, b, a = r1 - r2, g1 - g2, b1 - b2, a1 - a2
    return (r * r + g * g + b * b + a * a) ** 0.5

def edge_distance(e1, e2):
    return sum(pixel_distance(p1, p2) for p1, p2 in zip(e1, e2)) / len(e1)

class Tile(object):
    def __init__(self, path):
        self.path = path
        self.surface = cairo.ImageSurface.create_from_png(path)
        self.data = self.surface.get_data()
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        self.n = [self.get(x, 0) for x in range(self.width)]
        self.e = [self.get(self.width - 1, y) for y in range(self.height)]
        self.s = [self.get(x, self.height - 1) for x in range(self.width)]
        self.w = [self.get(0, y) for y in range(self.height)]
    def get(self, x, y):
        i = (self.width * y + x) * 4
        return tuple(ord(x) for x in self.data[i:i+4])
    def draw(self, dc, x, y):
        dc.set_source_surface(self.surface, x, y)
        dc.paint()
    def __repr__(self):
        return 'Tile(%r)' % self.path

class TileSet(object):
    def __init__(self, path):
        tiles = []
        for name in os.listdir(path):
            if not name.lower().endswith('.png'):
                continue
            tile = Tile(os.path.join(path, name))
            tiles.append(tile)
        self.path = path
        self.tiles = tiles
        self.neighbors = self.compute_neighbors(8)
    def compute_neighbors(self, threshold):
        result = defaultdict(set)
        for t1 in self.tiles:
            for t2 in self.tiles:
                if edge_distance(t1.n, t2.s) < threshold:
                    result[(t1, N)].add(t2)
                if edge_distance(t1.e, t2.w) < threshold:
                    result[(t1, E)].add(t2)
                if edge_distance(t1.s, t2.n) < threshold:
                    result[(t1, S)].add(t2)
                if edge_distance(t1.w, t2.e) < threshold:
                    result[(t1, W)].add(t2)
        return result
    def random(self):
        return random.choice(self.tiles)

class Model(object):
    def __init__(self, tiles, width, height, grid=None, scores=None, counts=None):
        self.tiles = tiles
        self.width = width
        self.height = height
        if grid:
            self.grid = dict(grid)
        else:
            self.grid = {}
            for y in range(self.height):
                for x in range(self.width):
                    self.grid[(x, y)] = self.tiles.random()
        if scores:
            self.scores = dict(scores)
        else:
            self.scores = {}
            for y in range(self.height):
                for x in range(self.width):
                    self.scores[(x, y)] = self.check(x, y)
        if counts:
            self.counts = dict(counts)
        else:
            self.counts = dict((tile, 0) for tile in self.tiles.tiles)
            for y in range(self.height):
                for x in range(self.width):
                    self.counts[self.grid[(x, y)]] += 1
    def update_scores(self, x, y):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx and dy:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) not in self.scores:
                    continue
                self.scores[(nx, ny)] = self.check(nx, ny)
    def do_move(self):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.scores[(x, y)]:
                break
        t = self.grid[(x, y)]
        self.grid[(x, y)] = self.tiles.random()
        self.counts[t] -= 1
        self.counts[self.grid[(x, y)]] += 1
        self.update_scores(x, y)
        return (x, y, t)
    def undo_move(self, undo):
        x, y, t = undo
        self.counts[t] += 1
        self.counts[self.grid[(x, y)]] -= 1
        self.grid[(x, y)] = t
        self.update_scores(x, y)
    def energy(self):
        counts = self.counts.values()
        m = float(self.width * self.height) / len(counts)
        mse = 0
        for count in counts:
            mse += (count - m) ** 2
        mse = mse ** 0.5
        total = sum(self.scores.values())
        if total == 0:
            return 0
        return total + mse * 10
    def copy(self):
        return Model(self.tiles, self.width, self.height, self.grid, self.scores)
    def render(self):
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
            self.width * TILE_SIZE, self.height * TILE_SIZE)
        dc = cairo.Context(surface)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[(x, y)]
                tile.draw(dc, x * TILE_SIZE, y * TILE_SIZE)
        return surface
    def check(self, x, y):
        result = 0
        grid = self.grid
        neighbors = self.tiles.neighbors
        tile = grid[(x, y)]
        if (x, y - 1) in grid and grid[(x, y - 1)] not in neighbors[(tile, N)]:
            result += 1
        if (x + 1, y) in grid and grid[(x + 1, y)] not in neighbors[(tile, E)]:
            result += 1
        if (x, y + 1) in grid and grid[(x, y + 1)] not in neighbors[(tile, S)]:
            result += 1
        if (x - 1, y) in grid and grid[(x - 1, y)] not in neighbors[(tile, W)]:
            result += 1
        return result
    def best(self, x, y):
        lookup = defaultdict(int)
        grid = self.grid
        neighbors = self.tiles.neighbors
        if (x, y - 1) in grid:
            for t in neighbors[grid[(x, y - 1)], S]:
                lookup[t] += 1
        if (x + 1, y) in grid:
            for t in neighbors[grid[(x + 1, y)], W]:
                lookup[t] += 1
        if (x, y + 1) in grid:
            for t in neighbors[grid[(x, y + 1)], N]:
                lookup[t] += 1
        if (x - 1, y) in grid:
            for t in neighbors[grid[(x - 1, y)], E]:
                lookup[t] += 1
        hi = max(lookup.values())
        return [k for k, v in lookup.iteritems() if v >= hi]
    def update(self):
        positions = [(x, y) for y in range(self.height) for x in range(self.width)]
        random.shuffle(positions)
        result = 0
        for x, y in positions:
            if self.check(x, y):
                self.grid[(x, y)] = random.choice(self.best(x, y))
                result += 1
        return result

def main():
    tiles = TileSet('png')
    model = Model(tiles, WIDTH, HEIGHT)
    model = anneal.anneal(model, 2, 0.01, 1000000)
    surface = model.render()
    surface.write_to_png('output.png')

if __name__ == '__main__':
    main()
