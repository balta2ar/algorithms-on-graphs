#!/usr/bin/python3

import sys
from queue import PriorityQueue

class DijkstraBidirectional:
    def __init__(self, n, m):
        self.n = n                              # Number of nodes
        self.m = m
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        #self.visited = [False]*n                  # visited[v] == True iff v was visited by forward or backward search
        self.visited = [[False]*n, [False]*n]      # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search
        self.parent = [[None]*n, [None]*n]      # Used for backtracking
        self.best_path_len = self.inf

        self.adj = None
        self.cost = None

    def clear(self):
        """Reinitialize the data structures for the next query after the previous query."""
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            #self.parent[0][v] = self.parent[1][v] = None
            self.visited[0][v] = self.visited[1][v] = False
        #del self.workset[0:len(self.workset)]
        self.workset = []
        self.best_path_len = self.inf

    def query(self, adj, cost, source, target):
        if source == target:
            return 0

        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]

        self.adj = adj
        self.cost = cost

        self.dist[0][source] = self.dist[1][target] = 0
        queue[0].put((0, source))
        queue[1].put((0, target))

        while not queue[0].empty() or not queue[1].empty():
            dist = self.do_iteration(queue, 0, source, target)
            if dist is not None:
                return dist

            dist = self.do_iteration(queue, 1, source, target)
            if dist is not None:
                return dist

        if self.best_path_len < self.inf:
            return self.get_shortest_path(source, target)

        return -1

    def do_iteration(self, queue, side, source, target):
        u = self.get_min(queue, side)
        if u is None:
            return None

        self.visit(queue, side, u)

        if self.can_stop(side, u):
            return self.get_shortest_path(source, target)
        return None

    def visit(self, queue, side, u):
        neighbors = self.adj[side][u]

        for v_index, v in enumerate(neighbors):
            alt = self.dist[side][u] + self.cost[side][u][v_index]

            if alt < self.dist[side][v]:
                self.dist[side][v] = alt
                self.parent[side][v] = u
                queue[side].put((alt, v))
                self.workset.append(v)

            # update self.best_path_len (mu) if necessary
            other_side = 1 - side
            if self.dist[other_side][v] < self.inf:
                new_best_path_len = self.cost[side][u][v_index] + \
                    self.dist[side][u] + self.dist[other_side][v]

                if new_best_path_len < self.best_path_len:
                    self.best_path_len = new_best_path_len

        self.visited[side][u] = True
        self.workset.append(u)

    def can_stop(self, side, u):
        other_side = 1 - side
        return self.visited[other_side][u]

    def get_min(self, queue, side):
        if queue[side].empty():
            return None
        _, u = queue[side].get()
        return u

    def get_shortest_path(self, source, target):
        dist = self.inf
        u_best = -1

        for u in self.workset:
            candidate_dist = self.dist[0][u] + self.dist[1][u]
            if candidate_dist < dist:
                u_best = u
                dist = candidate_dist

        # path = []
        # last = u_best
        #
        # while last != source:
        #     path.append(last)
        #     last = self.parent[0][last]
        # path.reverse()
        #
        # last = u_best
        # while last != target:
        #     last = self.parent[1][last]
        #     path.append(last)

        return dist


class DijkstraOnedirectional:
    def __init__(self, n, m):
        self.n = n                              # Number of nodes
        self.m = m
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        self.visited = [False]*n                  # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search
        self.parent = [[None]*n, [None]*n]      # Used for backtracking

        self.adj = None
        self.cost = None

    def clear(self):
        """
        Reinitialize the data structures for the next query after the previous query.
        """
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            self.parent[0] = self.parent[1] = None
            self.visited[v] = False
        del self.workset[0:len(self.workset)]

    def query(self, adj, cost, source, target):
        if source == target:
            return 0

        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]

        self.adj = adj
        self.cost = cost

        self.dist[0][source] = 0
        queue[0].put((0, source))

        while not queue[0].empty():
            _, u = queue[0].get()
            self.visit(queue, u)

        if self.dist[0][target] != self.inf:
            return self.backtrack(source, target)

        return -1

    def visit(self, queue, u):
        """
        Try to relax the distance to node u from direction side by value dist.
        """
        neighbors = self.adj[0][u]
        for v_index, v in enumerate(neighbors):
            alt = self.dist[0][u] + self.cost[0][u][v_index]

            if alt < self.dist[0][v]:
                self.dist[0][v] = alt
                self.parent[0][v] = u
                queue[0].put((alt, v))

        self.visited[u] = True
        self.workset.append(u)

    def backtrack(self, source, target):
        path = []

        current = target
        while current != source:
            path.append(current)
            current = self.parent[0][current]
        path.append(current)

        #print(list(reversed(path)))
        return self.dist[0][target]


def readl():
    return map(int, sys.stdin.readline().split())


def read_from_stdin():
    n, m = readl()
    adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
    cost = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for _ in range(m):
        u, v, c = readl()
        adj[0][u-1].append(v-1)
        cost[0][u-1].append(c)
        adj[1][v-1].append(u-1)
        cost[1][v-1].append(c)

    return n, m, adj, cost


def main():
    n, m, adj, cost = read_from_stdin()
    t, = readl()

    alg = 'bi'
    if len(sys.argv) > 1:
        alg = sys.argv[1]

    if alg == 'one':
        bidij = DijkstraOnedirectional(n, m)
    elif alg == 'bi':
        bidij = DijkstraBidirectional(n, m)
    else:
        print('Unknown algorithm: %s' % alg)

    for _ in range(t):
        s, t = readl()
        print(bidij.query(adj, cost, s-1, t-1))


if __name__ == '__main__':
    main()
