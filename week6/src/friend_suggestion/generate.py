import sys
#from random import randint, seed
import random


MAX_WIDTH = 100000
MAX_HEIGHT = 100000


def generate_graph_coords(n, m):
    x = [random.randint(0, MAX_WIDTH) for _ in range(n)]
    y = [random.randint(0, MAX_HEIGHT) for _ in range(n)]

    adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
    cost = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for _ in range(m):
        u, v, c = readl()
        adj[0][u-1].append(v-1)
        cost[0][u-1].append(c)
        adj[1][v-1].append(u-1)
        cost[1][v-1].append(c)

    return x, y, adj, cost


def print_graph(n, m, x, y, adj, cost):
    pass


def print_queries(m, queries_count):
    pass


def main():
    n, m, queries_count, seed = sys.argv[1:]
    n, m, queries_count, seed = int(n), int(m), int(queries_count), int(seed)

    random.seed(seed)
    x, y, adj, cost = generate_graph_coords(n, m)
    print_graph(n, m, x, y, adj, cost)
    print_queries(n, queries_count)


if __name__ == '__main__':
    main()
