import numpy as np
from pyMaze import maze, agent
import random
from math import sqrt

# -----------------------------------------------------------------------

# Maze parameters, width and height of maze
MAZE_WIDTH = 15
MAZE_HEIGHT = 15

# Start and goal position in maze
START_POSITION = (MAZE_WIDTH, MAZE_HEIGHT)
GOAL_POSITION = (1, 1)

# Max number of moves in maze and number of agents
NUM_MOVES = MAZE_WIDTH * MAZE_HEIGHT
NUM_AGENTS = 200

# Parameters for genetic algorithm
MUTATION_RATE = 0.2
SELECTION_CUTOFF = 0.1

# Move directions North - N, South - S, East - E, West - W
DIRECTION_OPTIONS = ['E', 'W', 'N', 'S']

# Generation limit, stops the evaluation when more than GENERATION_LIMIT generations are created
GENERATION_LIMIT = 100

# -----------------------------------------------------------------------


class Agent:
    def __init__(self):
        # Agent properties
        self.fitness = 0
        self.move_list = []
        self.visited_positions = []
        self.x, self.y = START_POSITION
        self.win = False
        self.can_walk = True

    # method for move agents by direction to the next position (x,y)
    def move(self, direction):
        if direction == 'E':
            self.y = self.y + 1
        elif direction == 'W':
            self.y = self.y - 1
        elif direction == 'N':
            self.x = self.x - 1
        elif direction == 'S':
            self.x = self.x + 1

    # next_move method, check if the next move is possible and make a move
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

        if maze_map[(self.x, self.y)][move] == 1 and next_position not in self.visited_positions:
            self.visited_positions.append((self.x, self.y))
            self.move(move)
            return
        else:
            if maze_map[(self.x, self.y)][move] == 1:
                directions = [k for k, v in maze_map[(self.x, self.y)].items() if v == 1]
                directions.remove(move)

                if len(directions) < 1:
                    self.can_walk = False
                    return
                else:
                    tmp = random.choice(directions)
                    self.move_list[turn] = tmp
                    self.next_move(tmp,maze_map,turn)
                    return
            else:
                self.fitness += 200


class GeneticApplication:
    def __init__(self):
        # Genetic Application properties
        self.maze = maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.maze.CreateMaze()
        self.agents = [Agent() for _ in range(NUM_AGENTS)]
        self.turn = 1
        self.generation = 1

    # initialization method of the initial population of agents by a random array of directions
    def init_agents(self):
        for i in self.agents:
            i.move_list = generate_random_moves()

    # method that sets up the next generation of agents and reset turn, increase generation counter
    def next_generation(self, moves_list):
        self.turn = 1
        self.generation += 1

        self.agents = [Agent() for _ in range(NUM_AGENTS)]
        for i, m in enumerate(moves_list):
            self.agents[i].move_list = m

        print("## {} generation created ##".format(self.generation))
        # sleep(0.1)

    # evaluate method that in loop make move, calculate distance, perform selection, crossover,
    # mutation, next generation and  check if someone reach the goal
    def evaluate(self):
        while True:
            # if no one agent cant move, or it is last turn
            if self.turn == NUM_MOVES or max(a.can_walk for a in self.agents) is False:

                # if generation counter hits the generation limit, then stop evaluation and program
                if self.generation == GENERATION_LIMIT:
                    print('No agent found its path through the maze in {} generations'.format(GENERATION_LIMIT))
                    break

                # if any agents found path, then stop evaluation and show solution
                if any(a.win for a in self.agents) is True:
                    print('The agents found path through the maze')
                    break

                # calculate fitness for every agent in generation
                for a in self.agents:
                    a.fitness = calculate_distance((a.x, a.y), GOAL_POSITION)

                sum_fitness = 0
                for a in self.agents:
                    sum_fitness += a.fitness

                # sort agents by fitness
                self.agents.sort(key=lambda x: x.fitness)

                print('Best fitness of {} generation is {} and average fitness of population is {}'
                      .format(self.generation, self.agents[0].fitness, sum_fitness / NUM_AGENTS))

                # stores all moves arrays from every agent for next generation
                moves_list = []

                # selection and crossover
                for j in range(int(len(self.agents) * SELECTION_CUTOFF)):
                    if j == len(self.agents):
                        continue
                    if len(moves_list) >= NUM_AGENTS:
                        continue

                    for k in range(j + 1, len(self.agents)):
                        if len(moves_list) >= NUM_AGENTS:
                            continue

                        # Select two agents for crossover with every agent
                        better_agent = self.agents[j].move_list
                        worse_agent = self.agents[k].move_list
                        moves_list.append(crossover(better_agent, worse_agent))

                moves_list = np.array(moves_list)
                # mutation, pass moves_list, change some moves in arrays
                moves_list = mutate(moves_list)

                # call next generation
                self.next_generation(moves_list)

            # perform moves with agents
            for a in self.agents:
                move = a.move_list[self.turn - 1]
                a.next_move(move, self.maze.maze_map, self.turn - 1)

            # checks agents position with goal position
            for a in self.agents:
                if (a.x, a.y) == GOAL_POSITION:
                    a.win = True
                    a.can_walk = False

            # increase turn
            self.turn += 1


# -----------------------------------------------------------------------
# Functions

# Generate random moves function
def generate_random_moves(turns=NUM_MOVES):
    # Generate array of random moves North, South, East, West
    return np.array(random.choices(DIRECTION_OPTIONS, k=turns))


# Distance function
def calculate_distance(point1, point2):
    # Calculate distance function between agents position and goal position
    # if distance is equal to 0 then agents position and goal position is same

    # manhattan distance (squares between two points)
    dist = abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])

    # euclidean distance (straight line between two points)
    # dist = sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return dist


# Crossover function
def crossover(array1, array2):
    # generates random number between range 0 and length of array of moves
    # and use it for split array1 and array2 for crossover
    # returns a new array which is composed of the two moves arrays
    cut_point = random.randrange(0, len(array1) - 1)

    if random.random() >= 0.05:
        new_arr = np.concatenate((array1[:cut_point], array2[cut_point:]))
    else:
        new_arr = np.concatenate((array2[:cut_point], array1[cut_point:]))

    return new_arr


# Mutation function
def mutate(array):
    # if random generated number between 0-1 is less or equal as MUTATION_RATE then we perform mutation
    # then randomly selects which places are to be mutated in moves from agents
    # and returns new array with moves (every row is one moves list for agent and column is move in current turn)
    # for the next generation of agents
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

# -----------------------------------------------------------------------


if __name__ == '__main__':
    genetic_app = GeneticApplication()
    genetic_app.init_agents()

    genetic_app.evaluate()

    a_goal = [a for a in genetic_app.agents if a.win is True]

    if a_goal:
        total_winners = len([i for i in genetic_app.agents if i.win is True])
        print('{}% agents reach goal destination'.format((total_winners / NUM_AGENTS) * 100))

        a = agent(genetic_app.maze, footprints=True)
        genetic_app.maze.tracePath({a: a_goal[0].visited_positions})
        genetic_app.maze.run()
