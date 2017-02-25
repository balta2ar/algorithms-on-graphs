#!/usr/bin/python3

import sys
from queue import PriorityQueue

class DijkstraBidirectional:
    def __init__(self, n):
        self.n = n                              # Number of nodes
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        self.visited = [False]*n                  # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search

    def clear(self):
        """Reinitialize the data structures for the next query after the previous query."""
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            self.visited[v] = False
        del self.workset[0:len(self.workset)]

    def visit(self, q, side, v, dist):
        """Try to relax the distance to node v from direction side by value dist."""
        # Implement this method yourself
        pass

    def query(self, adj, cost, source, target):
        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]
        self.visit(queue, 0, source, 0)
        self.visit(queue, 1, target, 0)
        # Implement the rest of the algorithm yourself
        return -1

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
            self.visited[v] = False
        del self.workset[0:len(self.workset)]

    def visit(self, queue, side, u):
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

    def query(self, adj, cost, source, target):
        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]

        self.adj = adj
        self.cost = cost

        self.dist[0][source] = 0
        queue[0].put((0, source))

        while not queue[0].empty():
            _, u = queue[0].get()
            self.visit(queue, 0, u)

        if self.dist[0][target] != self.inf:
            return self.backtrack(source, target)

        return -1

    def backtrack(self, source, target):
        # path = []
        #
        # current = target
        # while current != source:
        #     path.append(current)
        #     current = self.parent[0][current]
        # path.append(current)

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

    bidij = DijkstraOnedirectional(n, m)
    for _ in range(t):
        s, t = readl()
        print(bidij.query(adj, cost, s-1, t-1))


if __name__ == '__main__':
    main()
