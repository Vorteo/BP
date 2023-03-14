from pyMaze import maze, COLOR, agent, textLabel
import random
import math


def generate_random_moves(num_of_steps):
    # right, left, up, down
    move_options = ['E', 'W', 'N', 'S']
    return random.choices(move_options, k=num_of_steps)


def calculate_distance(x1, x2):
    dist = math.dist(x1, x2)
    return dist


if __name__ == '__main__':
    m = maze(20, 30)
    m.CreateMaze()
    a = agent(m, footprints=True, filled=True)
    b = agent(m, footprints=True)
    # path = ''.join(generate_random_moves(100))
    # m.tracePath({a: path, b:m.path})
    print(m.maze_map)
    m.run()

