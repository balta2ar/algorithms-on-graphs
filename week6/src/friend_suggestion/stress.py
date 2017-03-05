#!/usr/bin/python3

import sys

from friend_suggestion import DijkstraOnedirectional
from friend_suggestion import DijkstraBidirectional
from dist_with_coords import AStarOnedirectional
from dist_with_coords import AStarBidirectional
from landmarks import BreadthFirstSearchOneToAll
from dijkstra import ReferenceDijkstra


def readl():
    return map(int, sys.stdin.readline().split())


def read_from_stdin_reversed():
    n, m = readl()

    x = [0 for _ in range(n)]
    y = [0 for _ in range(n)]
    for i in range(n):
        a, b = readl()
        x[i] = a
        y[i] = b

    adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
    cost = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for _ in range(m):
        u, v, c = readl()
        adj[0][u-1].append(v-1)
        cost[0][u-1].append(c)
        adj[1][v-1].append(u-1)
        cost[1][v-1].append(c)

    return n, m, adj, cost, x, y


def main():
    n, m, adj, cost, x, y = read_from_stdin_reversed()
    t, = readl()

    algs = [
        ('DijkOne', DijkstraOnedirectional(n, m, adj, cost)),
        ('DijkBi', DijkstraBidirectional(n, m, adj, cost)),
        ('AStarOne', AStarOnedirectional(n, m, adj, cost, x, y)),
        ('AStarBi', AStarBidirectional(n, m, adj, cost, x, y)),
        ('BFS', BreadthFirstSearchOneToAll(n, m, adj, cost)),
        # ('RefDijk', ReferenceDijkstra(n, m, adj, cost)),
    ]

    template = '%15s'
    results = [template % ''] + [template % name for name, _ in algs]
    print(''.join(results))

    for _ in range(t):
        s, t = readl()
        results = [alg.query(s-1, t-1) for name, alg in algs]
        mismatch = 'MISMATCH' if len(set(results)) > 1 else ''
        results = [template % mismatch] + [template % result for result in results]
        print(''.join(results))
        #print(astar.query(s-1, t-1))


if __name__ == '__main__':
    main()
