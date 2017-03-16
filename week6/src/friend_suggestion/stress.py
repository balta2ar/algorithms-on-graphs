#!/usr/bin/python3

import sys
import argparse
import random
import time
from functools import partial

from friend_suggestion import DijkstraOnedirectional
from friend_suggestion import DijkstraBidirectional
from dist_with_coords import AStarOnedirectional
from dist_with_coords import AStarBidirectional
from dist_preprocess_small import DistPreprocessSmall
from landmarks import BreadthFirstSearchOneToAll
from landmarks import LandmarksAStarOnedirectional
from landmarks import LandmarksAStarBidirectional
from dijkstra import ReferenceDijkstra


TEMPLATE = '%15s'
TIMES = '%15.5f'
SEPARATOR = ' '


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


def profile_execution(method):
    start = time.time()
    result = method()
    delta = time.time() - start
    return delta, result


def verify_all(algs, s, t, stop, hide_results, mismatch_only, profile):
    #results = [alg.query(s-1, t-1) for name, alg in algs]
    results = [profile_execution(partial(alg.query, s-1, t-1))
               for name, alg in algs]
    deltas, results = zip(*results)

    len_results = len(set(results))
    if not hide_results:
        if (len_results > 1) or (len_results == 1 and not mismatch_only):
            mismatch = 'MISMATCH' if len_results > 1 else ''
            results = [TEMPLATE % mismatch] + [TEMPLATE % result for result in results]
            results.append(TEMPLATE % ('%s %s' % (s, t),))
            print(SEPARATOR.join(results))

    if profile:
        deltas = [TEMPLATE % '<time>'] + [TIMES % delta for delta in deltas]
        print(SEPARATOR.join(deltas))

    if stop and len_results != 1:
        raise MistatchException()
    #print(astar.query(s-1, t-1))


def run_embedded_queries(algs, t, stop, hide_results, mismatch_only, profile):
    for _ in range(t):
        s, t = readl()
        verify_all(algs, s, t, stop, hide_results, mismatch_only, profile)


def run_random_queries(algs, n, stop, seed, random_queries, hide_results, mismatch_only, profile):
    print('Executing %d random random queries (seed %s)' % \
            (random_queries, seed))
    for _ in range(random_queries):
        s, t = random.randint(1, n), random.randint(1, n)
        verify_all(algs, s, t, stop, hide_results, mismatch_only, profile)


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
    parser.add_argument('--profile', default=False, action='store_true',
                        help='Profile each algorithm query execution')
    parser.add_argument('--hide-results', default=False, action='store_true',
                        help='Hide query results (calculated distances)')
    parser.add_argument('--mismatch-only', default=False, action='store_true',
                        help='Show only mismatched results')
    return parser.parse_args()


def main():
    args = parse_args()

    n, m, adj, cost, x, y = read_from_stdin_reversed()
    t, = readl()

    algs = [
        #('BFS', BreadthFirstSearchOneToAll(n, m, adj, cost)),
        ('DijkOne', DijkstraOnedirectional(n, m, adj, cost)),
        ('AStarOne', AStarOnedirectional(n, m, adj, cost, x, y)),
        #('ALTOne', LandmarksAStarOnedirectional(n, m, adj, cost, x, y)),
        ('DijkBi', DijkstraBidirectional(n, m, adj, cost)),
        ('AStarBi', AStarBidirectional(n, m, adj, cost, x, y)),
        ('CHsimple', DistPreprocessSmall(n, m, adj, cost, x, y)),
        #('ALTBi', LandmarksAStarBidirectional(n, m, adj, cost, x, y)),
        #('RefDijk', ReferenceDijkstra(n, m, adj, cost)),
    ]

    header = [TEMPLATE % ''] + [TEMPLATE % name for name, _ in algs] + [TEMPLATE % 's -> t']
    print(SEPARATOR.join(header))

    result = 0
    try:
        if not args.skip_embedded:
            run_embedded_queries(algs, t, args.stop,
                                 args.hide_results, args.mismatch_only,
                                 args.profile)

        if args.random_queries > 0:
            if args.seed is None:
                args.seed = random.randint(0, 1e9)
            random.seed(args.seed)
            run_random_queries(algs, n,
                               args.stop, args.seed, args.random_queries,
                               args.hide_results, args.mismatch_only,
                               args.profile)
    except MistatchException:
        print('Mismatch found, stopping (seed %s)' % args.seed)
        result = 1
    print(SEPARATOR.join(header))

    return result


if __name__ == '__main__':
    sys.exit(main())
