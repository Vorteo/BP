from pyMaze import maze, COLOR, agent, textLabel
import random
import math

NUM_MOVES = 200
NUM_AGENTS = 400

MUTATION_RATE = 0.2
SELECTION_CUTOFF = 0.1


def generate_random_moves(num_of_steps):
    # right, left, up, down
    move_options = ['E', 'W', 'N', 'S']
    return random.choices(move_options, k=num_of_steps)


def calculate_distance(x1, x2):
    dist = math.dist(x1, x2)
    return dist


def crossover():
    pass


def mutate():
    pass


def init_population():
    result = []

    for x in range(NUM_AGENTS):
        result.append(''.join(generate_random_moves(NUM_MOVES)))
    return result


if __name__ == '__main__':

    paths = init_population()

    m = maze(20, 20)
    m.CreateMaze()
    a = agent(m, footprints=True, filled=True,color=COLOR.red)
    b = agent(m, footprints=True)
    path = ''.join(generate_random_moves(100))
    # m.tracePath({a: path, b:m.path})
    for i in range(NUM_AGENTS):
        m.tracePath({a: paths[i]},delay=50)
    print(m.maze_map)
    m.run()

