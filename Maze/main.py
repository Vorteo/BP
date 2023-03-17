import numpy as np

from pyMaze import maze, COLOR, agent
import random
import math

MAZE_WIDTH = 25
MAZE_HEIGHT = 25
NUM_MOVES = MAZE_WIDTH * MAZE_HEIGHT
NUM_AGENTS = 100

START_POS = (MAZE_WIDTH, MAZE_HEIGHT)

MUTATION_RATE = 0.2
SELECTION_CUTOFF = 0.1


directions = ['E', 'W', 'N', 'S']

maze_map = None
turn = 1
generations = 1


class Agent:
    def __init__(self):
        self.move_list = []
        self.x, self.y = START_POS
        self.fitness = 0
        self.can_walk = True
        self.win = False

    def move(self, direction):
        if direction == 'E':
            self.y = self.y + 1
        elif direction == 'W':
            self.y = self.y - 1
        elif direction == 'N':
            self.x = self.x - 1
        elif direction == 'S':
            self.x = self.x + 1
        else:
            print('Unknown move')

    def check_next_move(self, move):
        values = None
        if self.can_walk:
            if (self.x, self.y) in maze_map:
                values = maze_map[(self.x, self.y)]
            else:
                self.can_walk = False
                return

            if values[move] == 1:
                self.move(move)
            else:
                self.can_walk = False
                self.fitness += 350
                return


def generate_random_moves(num_of_steps):
    return random.choices(directions, k=num_of_steps)


def calculate_distance(x1, x2):
    dist = math.dist(x1, x2)
    return dist


def crossover(list1, list2):
    cut_point = random.randrange(0, len(list1) - 1)
    if random.random() >= 0.05:
        new_list = list1[:cut_point] + list2[cut_point:]
    else:
        new_list = list2[:cut_point] + list1[cut_point:]

    return new_list


def mutate(array):
    if random.random() <= MUTATION_RATE:
        total = np.shape(array)[0] * np.shape(array)[1]

        amount_to_mutate = int(total * MUTATION_RATE)
        places = [random.randint(0, total - 1) for i in range(amount_to_mutate)]

        for ele in places:
            row = ele / NUM_MOVES
            column = ele % NUM_MOVES
            current = array[row, column]
            array[row, column] = random.choice(directions[directions!=current])

        return array
    else:
        return array


def next_generation(moves_lists):
    global turn, generations
    turn = 1
    generations += 1
    move_array = np.array(moves_lists)
    agents_ = [Agent() for i in range(NUM_AGENTS)]

    return move_array, agents_


if __name__ == '__main__':

    agents = [Agent() for i in range(NUM_AGENTS)]
    for a in agents:
        a.move_list = generate_random_moves(NUM_MOVES)

    m = maze(MAZE_WIDTH, MAZE_HEIGHT)
    m.CreateMaze()

    print(m.maze_map)
    maze_map = m.maze_map

    a = agent(m, footprints=True, filled=False, color=COLOR.red)

    while turn < NUM_MOVES or max(ag.can_walk for ag in agents) is not False:
        for i in agents:
            current_move = i.move_list[turn-1]
            i.check_next_move(current_move)
            if i.can_walk:
                a.position = (i.x, i.y)
        turn += 1

    for i in agents:
        i.fitness = calculate_distance((i.x, i.y), (1, 1))

    agents.sort(key=lambda x: x.fitness)
    print('Best fitness of {}'.format(agents[0].fitness))

    move_lists = []
    for j in range(agents * SELECTION_CUTOFF):
        if j == len(agents):
            continue

        for k in range(j + 1, len(agents)):
            better_agent = agents[j].move_list
            worse_agent = agents[k].move_list
            move_lists.append(crossover(better_agent, worse_agent))

    move_lists = np.array(move_lists)
    move_lists = mutate(move_lists)

    m.run()

