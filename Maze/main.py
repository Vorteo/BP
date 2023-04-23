from pyMaze import maze, COLOR, agent
import numpy as np
from scipy.spatial.distance import cityblock
import random
import sys

MAZE_WIDTH = 25
MAZE_HEIGHT = 25

# Start and goal position in maze
START_POSITION = (MAZE_WIDTH, MAZE_HEIGHT)
GOAL_POSITION = (1, 1)

# Max number of moves in maze and number of agents
NUM_MOVES = MAZE_WIDTH * MAZE_HEIGHT
NUM_AGENTS = 1000

# Mutation and Selection
MUTATION_RATE = 0.15
SELECTION_CUTOFF = 0.1

# Move directions North - N, South - S, East - E, West - W
MOVES_OPTIONS = ['E', 'W', 'N', 'S']

# Generation limit, stops the evaluation when more than GENERATION_LIMIT are created
GENERATION_LIMIT = 2000


class Agent:
    def __init__(self):
        self.x, self.y = START_POSITION
        self.fitness = 0
        self.move_array = []
        self.visited_positions = []
        self.win = False
        self.can_walk = True

    # method for move agents by direction to the next position [x, y]
    def move(self, direction):
        if direction == 'E':
            self.y = self.y + 1
        elif direction == 'W':
            self.y = self.y - 1
        elif direction == 'N':
            self.x = self.x - 1
        elif direction == 'S':
            self.x = self.x + 1

    # method returns a list of moves that do not lead to the already visited position
    def correct_moves(self, possible_moves):
        moves = []
        for d in possible_moves:
            if d == 'N':
                if (self.x - 1, self.y) not in self.visited_positions:
                    moves.append(d)
            if d == 'S':
                if (self.x + 1, self.y) not in self.visited_positions:
                    moves.append(d)
            if d == 'E':
                if (self.x, self.y + 1) not in self.visited_positions:
                    moves.append(d)
            if d == 'W':
                if (self.x, self.y - 1) not in self.visited_positions:
                    moves.append(d)

        return moves

    # method calculate and return the next position of agent
    def next_position(self, move):
        next_position = tuple()

        if move == 'E':
            next_position = (self.x, self.y + 1)
        elif move == 'W':
            next_position = (self.x, self.y - 1)
        elif move == 'N':
            next_position = (self.x - 1, self.y)
        elif move == 'S':
            next_position = (self.x + 1, self.y)

        return next_position

    # method checks if the next move is possible and perform him
    def next_move(self, move, maze_map, turn):
        if self.can_walk is False:
            return

        next_position = self.next_position(move)

        if maze_map[(self.x, self.y)][move] == 1 and next_position not in self.visited_positions:
            self.move(move)
        else:
            possible_moves = [k for k, v in maze_map[(self.x, self.y)].items() if v == 1]
            if len(possible_moves) == 1:
                self.can_walk = False
                self.fitness += 300
            else:
                correct_moves = self.correct_moves(possible_moves)
                remainder = set(correct_moves) - set(move)
                remainder = [i for i in remainder]

                if len(remainder) > 1:
                    choice = random.choice(remainder)
                    self.move_array[turn] = choice
                    self.move(choice)
                elif len(remainder) == 0:
                    self.can_walk = False
                else:
                    self.move_array[turn] = remainder[0]
                    self.move(remainder[0])


class GeneticApplication:
    def __init__(self):
        self.maze = maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.maze.CreateMaze()
        self.agents = [Agent() for _ in range(NUM_AGENTS)]
        self.turn = 1
        self.generation = 1

    # initialization method of the initial population of agents by a random array of moves
    def init_agents(self):
        for a in self.agents:
            a.move_array = self.generate_random_moves()

    # Generate random moves method
    @staticmethod
    def generate_random_moves(turns=NUM_MOVES):
        return np.array(random.choices(MOVES_OPTIONS, k=turns))

    # method that sets up the next generation of agents and reset turn, increase generation counter
    def next_generation(self, moves_lists):
        self.turn = 1
        self.generation += 1

        self.agents = [Agent() for _ in range(NUM_AGENTS)]
        for i, m in enumerate(moves_lists):
            self.agents[i].move_array = m

        print(f"## {self.generation} generation created ##")

    # evaluate method that in loop perform move, calculate distance, perform selection, crossover,
    # mutation, next generation and  check if someone reach the goal
    def evaluate(self):
        while True:
            if self.turn == NUM_MOVES or max(a.can_walk for a in self.agents) is False:
                if self.generation == GENERATION_LIMIT:
                    print(f'No agent found its path through the maze in {GENERATION_LIMIT} generations')
                    break

                sum_of_winners = len([i for i in genetic_app.agents if i.win is True])
                if (sum_of_winners / NUM_AGENTS) > 0.9:
                    print('The agents found path through the maze')
                    break

                # calculate fitness for every agent in generation
                for a in self.agents:
                    a.fitness += calculate_distance((a.x, a.y), GOAL_POSITION)

                sum_fitness = 0
                for a in self.agents:
                    sum_fitness += a.fitness

                # sort agents by fitness
                self.agents.sort(key=lambda x: x.fitness)

                print(f'Best fitness of {self.generation} generation is {self.agents[0].fitness} and average'
                      f' fitness of population is {sum_fitness / NUM_AGENTS:.3f}')

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
                        better_agent = self.agents[j].move_array
                        worse_agent = self.agents[k].move_array
                        moves_list.append(crossover(better_agent, worse_agent))

                moves_list = np.array(moves_list)
                # mutation, pass moves_list, change some moves in arrays
                moves_list = mutate(moves_list)

                # call next generation
                self.next_generation(moves_list)

            # perform moves with agents
            for a in self.agents:
                move = a.move_array[self.turn - 1]
                a.next_move(move, self.maze.maze_map, self.turn - 1)
                if a.win is not True:
                    a.visited_positions.append((a.x, a.y))

            # checks agents position with goal position
            for a in self.agents:
                if (a.x, a.y) == GOAL_POSITION:
                    a.win = True
                    a.can_walk = False

            # increase turn
            self.turn += 1


# Functions

# Distance function
# Calculate distance function between agents position and goal position
def calculate_distance(point1, point2):
    dist = cityblock(point2, point1)
    # dist = abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])
    return dist


# Crossover function
def crossover(array1, array2):
    # generates random number between range 0 and length of array of moves
    # and use it for split array1 and array2 for crossover
    # returns a new array which is composed of the two moves arrays
    cut_point = random.randint(0, len(array1) - 1)

    if random.random() < 0.95:
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
        total_elements = array.size

        amount_to_mutate = int(total_elements * MUTATION_RATE)
        indices = random.sample(range(total_elements), amount_to_mutate)

        for i in indices:
            row = i // NUM_MOVES
            column = i % NUM_MOVES
            current = array[row, column]
            array[row, column] = random.choice(MOVES_OPTIONS[MOVES_OPTIONS != current])

        return array
    else:
        return array


def update_variables():
    global MAZE_WIDTH, MAZE_HEIGHT, NUM_AGENTS, MUTATION_RATE, SELECTION_CUTOFF, GENERATION_LIMIT, START_POSITION
    
    variables = {
        "MAZE_WIDTH": MAZE_WIDTH,
        "MAZE_HEIGHT": MAZE_HEIGHT,
        "NUM_AGENTS": NUM_AGENTS,
        "MUTATION_RATE": MUTATION_RATE,
        "SELECTION_CUTOFF": SELECTION_CUTOFF,
        "GENERATION_LIMIT": GENERATION_LIMIT,
    }
    print("Do you want to change any variables? Press Enter to skip.")
    for var_name, var_value in variables.items():
        new_value = input(f"Enter new value for {var_name} (default is {var_value}): ")
        if new_value:
            if var_name == "MAZE_WIDTH":
                START_POSITION = (int(new_value), START_POSITION[1])
            elif var_name == "MAZE_HEIGHT":
                # Update START_POSITION[1] based on new value of MAZE_HEIGHT
                START_POSITION = (START_POSITION[0], int(new_value))
            variables[var_name] = type(var_value)(new_value)
    MAZE_WIDTH, MAZE_HEIGHT, NUM_AGENTS, MUTATION_RATE, SELECTION_CUTOFF, GENERATION_LIMIT = \
        variables["MAZE_WIDTH"], variables["MAZE_HEIGHT"],\
        variables["NUM_AGENTS"], variables["MUTATION_RATE"], variables["SELECTION_CUTOFF"], \
        variables["GENERATION_LIMIT"]

    print("Variables updated successfully!")


if __name__ == '__main__':
    update_variables()

    if "test" in sys.argv:
        solved_mazes = 0
        number_of_mazes = 0

        while True:
            number_of_mazes += 1

            genetic_app = GeneticApplication()
            genetic_app.init_agents()

            genetic_app.evaluate()

            a_goal = [a for a in genetic_app.agents if a.win is True]

            if a_goal:
                solved_mazes += 1

                total_winners = len([i for i in genetic_app.agents if i.win is True])
                print("\n")
                print('{0:.2f}% of agents reach goal destination'.format((total_winners / NUM_AGENTS) * 100))
                print('Solved mazes: {}, number of mazes: {}'.format(solved_mazes, number_of_mazes))
                print("\n")

                a = agent(genetic_app.maze, footprints=True)
                genetic_app.maze.tracePath({a: a_goal[0].visited_positions}, delay=80)
            else:
                for i in genetic_app.agents:
                    a = agent(genetic_app.maze, footprints=True, color=COLOR.red)
                    genetic_app.maze.tracePath({a: i.visited_positions}, delay=5)
    else:

        genetic_app = GeneticApplication()
        genetic_app.init_agents()

        genetic_app.evaluate()

        a_goal = [a for a in genetic_app.agents if a.win is True]

        if a_goal:
            total_winners = len([i for i in genetic_app.agents if i.win is True])
            print('{0:.2f}% of agents reach goal destination'.format((total_winners / NUM_AGENTS) * 100))
            print("\n")

            a = agent(genetic_app.maze, footprints=True)

            random_agent = random.choice(a_goal)
            genetic_app.maze.tracePath({a: random_agent.visited_positions}, delay=80)
        else:
            for i in genetic_app.agents:
                a = agent(genetic_app.maze, footprints=True, color=COLOR.red)
                genetic_app.maze.tracePath({a: i.visited_positions}, delay=5)

        genetic_app.maze.run()
