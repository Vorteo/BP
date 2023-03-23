import numpy as np
from pyMaze import maze, COLOR, agent
import random
from math import sqrt

# -----------------------------------------------------------------------
# Maze parameters, width and height of maze
MAZE_WIDTH = 10
MAZE_HEIGHT = 10

# Start and goal position in maze
START_POS = (MAZE_WIDTH, MAZE_HEIGHT)
GOAL_POS = (1, 1)

# Max number of moves in maze and number of agents
NUM_MOVES = MAZE_WIDTH * MAZE_HEIGHT
NUM_AGENTS = 900

# Parameters for genetic algorithm
MUTATION_RATE = 0.2
SELECTION_CUTOFF = 0.1

# Move directions == North - N, South - S, East - E, West - W
DIRECTION_OPTIONS = ['E', 'W', 'N', 'S']


# -----------------------------------------------------------------------


class Agent:
    fitness = 0
    can_walk = True
    win = False

    def __init__(self):
        self.move_list = []
        self.visited_positions = []
        self.x, self.y = START_POS

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

    def next_move(self, move, maze_map, turn):

        if self.can_walk is False:
            return

        next_position = tuple()

        if move == 'E':
            next_position = (self.x, self.y + 1)
        elif move == 'W':
            next_position = (self.x, self.y - 1)
        elif move == 'N':
            next_position = (self.x - 1, self.y)
        elif move == 'S':
            next_position = (self.x + 1, self.y)

        if (self.x, self.y) in maze_map:
            if maze_map[(self.x, self.y)][move] == 1 and next_position not in self.visited_positions:
                self.visited_positions.append((self.x, self.y))
                self.move(move)
            else:
                if next_position in self.visited_positions:
                    directions = [k for k, v in maze_map[(self.x, self.y)].items() if v == 1]
                    try:
                        directions.remove(move)
                    except:
                        return
                    if len(directions) < 1:
                        self.can_walk = False
                        self.fitness += 200
                        return
                    else:
                        tmp = random.choice(directions)
                        self.move_list[turn] = tmp
                        self.move(tmp)
        else:
            self.can_walk = False


class GeneticApplication:
    turn = 1
    generation = 1

    def __init__(self):
        self.maze = maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.maze.CreateMaze()

        self.agents = [Agent() for _ in range(NUM_AGENTS)]

    def init_population(self):
        for i in self.agents:
            i.move_list = generate_random_moves()

    def next_generation(self, moves_list):
        self.turn = 1
        self.generation += 1

        self.agents = [Agent() for _ in range(NUM_AGENTS)]
        for i, m in enumerate(moves_list):
            self.agents[i].move_list = m

    def evaluate(self):
        while True:

            if self.turn == NUM_MOVES or max(a.can_walk for a in self.agents) is False:

                if any(a.win for a in self.agents):
                    print('Maze solution found')
                    break

                for a in self.agents:
                    a.fitness = calculate_distance((a.x, a.y), GOAL_POS)

                self.agents.sort(key=lambda x: x.fitness)
                print('Best fitness of {} generation is {}'.format(self.generation, self.agents[0].fitness))

                moves_list = []
                for j in range(int(len(self.agents) * SELECTION_CUTOFF)):
                    if j == len(self.agents):
                        continue
                    if len(moves_list) >= NUM_AGENTS:
                        continue

                    for k in range(j + 1, len(self.agents)):
                        if len(moves_list) >= NUM_AGENTS:
                            continue
                        better_agent = self.agents[j].move_list
                        worse_agent = self.agents[k].move_list
                        moves_list.append(crossover(better_agent, worse_agent))

                moves_list = np.array(moves_list)
                moves_list = mutate(moves_list)

                self.next_generation(moves_list)

            for a in self.agents:
                move = a.move_list[self.turn - 1]
                a.next_move(move, self.maze.maze_map, self.turn - 1)

            for a in self.agents:
                if (a.x, a.y) == GOAL_POS:
                    a.win = True
                    a.can_walk = False
                    print('Someone reach the goal destination!')

            self.turn += 1


# -----------------------------------------------------------------------
# Generate array of random moves Up, Down, Left and Right as North, South, East, West
def generate_random_moves():
    return np.array(random.choices(DIRECTION_OPTIONS, k=NUM_MOVES))


# Calculate distance between two points
def calculate_distance(point1, point2):
    dist = abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])
    # dist = sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return dist


# crossover
def crossover(array1, array2):
    cut_point = random.randrange(0, len(array1) - 1)

    if random.random() >= 0.05:
        new_arr = np.concatenate((array1[:cut_point], array2[cut_point:]))
    else:
        new_arr = np.concatenate((array2[:cut_point], array1[cut_point:]))

    return new_arr


# mutation
def mutate(array):
    if random.random() <= MUTATION_RATE:
        total = np.shape(array)[0] * np.shape(array)[1]

        amount_to_mutate = int(total * MUTATION_RATE)
        places = [random.randint(0, total - 1) for _ in range(amount_to_mutate)]

        for p in places:
            row = p // NUM_MOVES
            column = p % NUM_MOVES
            current = array[row, column]
            array[row, column] = random.choice(DIRECTION_OPTIONS[DIRECTION_OPTIONS != current])

        return array
    else:
        return array


if __name__ == '__main__':
    genetic_app = GeneticApplication()
    genetic_app.init_population()

    genetic_app.evaluate()

    a_goal = [a for a in genetic_app.agents if a.win is True]

    a = agent(genetic_app.maze, footprints=True)
    genetic_app.maze.tracePath({a: a_goal[0].visited_positions})

    genetic_app.maze.run()
