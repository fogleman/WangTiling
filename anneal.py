import math
import random

def anneal(state, max_temp, min_temp, steps):
    factor = -math.log(float(max_temp) / min_temp)
    energy = state.energy()
    previous_energy = energy
    best_energy = energy
    best_state = state.copy()
    for step in xrange(steps):
        print step, steps, best_energy
        temp = max_temp * math.exp(factor * step / steps)
        undo_data = state.do_move()
        energy = state.energy()
        change = energy - previous_energy
        if change > 0 and math.exp(-change / temp) < random.random():
            state.undo_move(undo_data)
        else:
            previous_energy = energy
            if energy < best_energy:
                best_energy = energy
                best_state = state.copy()
                if energy <= 0:
                    break
    return best_state
