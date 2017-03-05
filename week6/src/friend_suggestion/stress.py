#!/usr/bin/python3

import sys
import argparse
import random

from friend_suggestion import DijkstraOnedirectional
from friend_suggestion import DijkstraBidirectional
from dist_with_coords import AStarOnedirectional
from dist_with_coords import AStarBidirectional
from landmarks import BreadthFirstSearchOneToAll
from dijkstra import ReferenceDijkstra


TEMPLATE = '%15s'


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


class MistatchException(Exception):
    pass


def verify_all(algs, s, t, stop):
    results = [alg.query(s-1, t-1) for name, alg in algs]
    len_results = len(set(results))
    mismatch = 'MISMATCH' if len_results > 1 else ''
    results = [TEMPLATE % mismatch] + [TEMPLATE % result for result in results]
    results.append(TEMPLATE % ('%s %s' % (s, t),))
    print(''.join(results))
    if stop and len_results != 1:
        raise MistatchException()
    #print(astar.query(s-1, t-1))


def run_embedded_queries(stop, algs, t):
    for _ in range(t):
        s, t = readl()
        verify_all(algs, s, t, stop)


def run_random_queries(stop, seed, random_queries, algs, n):
    if seed is None:
        seed = random.randint(0, 1e9)
    random.seed(seed)
    print('Executing %d random random queries (seed %s)' % \
            (random_queries, seed))
    for _ in range(random_queries):
        s, t = random.randint(1, n), random.randint(1, n)
        verify_all(algs, s, t, stop)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--random-queries', type=int, default=0,
                        help='Number of additional random queries')
    parser.add_argument('--seed', type=int, default=None,
                        help='Initial seed')
    parser.add_argument('--skip-embedded', default=False, action='store_true',
                        help='If True, skips embedder queries into the graph')
    parser.add_argument('--stop', default=False, action='store_true',
                        help='Stop on first mismatch occurence')
    return parser.parse_args()


def main():
    args = parse_args()

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

    results = [TEMPLATE % ''] + [TEMPLATE % name for name, _ in algs] + [TEMPLATE % 's -> t']
    print(''.join(results))

    try:
        if not args.skip_embedded:
            run_embedded_queries(args.stop, algs, t)

        if args.random_queries > 0:
            run_random_queries(args.stop, args.seed, args.random_queries, algs, n)
    except MistatchException:
        print('Mismatch found, stopping')


if __name__ == '__main__':
    main()
