#!/usr/bin/python3

import sys
from queue import PriorityQueue


# -----------------------------------------------------------------------------


class DijkstraOnedirectional:
    def __init__(self, n, m, adj, cost):
        self.n = n                              # Number of nodes
        self.m = m
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        self.visited = [False]*n                  # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search
        self.parent = [[None]*n, [None]*n]      # Used for backtracking

    def clear(self):
        """
        Reinitialize the data structures for the next query after the previous query.
        """
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            #self.parent[0] = self.parent[1] = None
            self.visited[v] = False
        self.workset = []

    def query(self, source, target):
        if source == target:
            return 0

        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]

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
            print(v, file=sys.stderr)
            alt = self.dist[0][u] + self.cost[0][u][v_index]

            if alt < self.dist[0][v]:
                self.dist[0][v] = alt
                #self.parent[0][v] = u
                queue[0].put((alt, v))
                self.workset.append(v)

        self.visited[u] = True
        self.workset.append(u)

    def backtrack(self, source, target):
        # path = []

        # current = target
        # while current != source:
        #     path.append(current)
        #     current = self.parent[0][current]
        # path.append(current)

        #print(list(reversed(path)))
        return self.dist[0][target]


# -----------------------------------------------------------------------------


class DijkstraBidirectional:
    def __init__(self, n, m, adj, cost):
        self.n = n                              # Number of nodes
        self.m = m
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        self.visited = [[False]*n, [False]*n]      # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search
        self.parent = [[None]*n, [None]*n]      # Used for backtracking

    def clear(self):
        """Reinitialize the data structures for the next query after the previous query."""
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            self.visited[0][v] = self.visited[1][v] = False
        self.workset = []

    def query(self, source, target):
        if source == target:
            return 0

        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]

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

        return -1

    def do_iteration(self, queue, side, source, target):
        if queue[side].empty():
            return None
        _, u = queue[side].get()

        self.visit(queue, side, u)

        other_side = 1 - side
        if self.visited[other_side][u]:
            return self.get_shortest_path(source, target)

        return None

    def visit(self, queue, side, u):
        local_adj = self.adj
        local_dist = self.dist
        local_cost = self.cost
        local_parent = self.parent
        local_workset = self.workset

        neighbors = local_adj[side][u]

        for v_index, v in enumerate(neighbors):
            print(v, file=sys.stderr)
            alt = local_dist[side][u] + local_cost[side][u][v_index]

            if alt < local_dist[side][v]:
                local_dist[side][v] = alt
                local_parent[side][v] = u
                queue[side].put((alt, v))
                local_workset.append(v)

        self.visited[side][u] = True
        local_workset.append(u)

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


# -----------------------------------------------------------------------------


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
        bidij = DijkstraOnedirectional(n, m, adj, cost)
    elif alg == 'bi':
        bidij = DijkstraBidirectional(n, m, adj, cost)
    else:
        print('Unknown algorithm: %s' % alg)

    for _ in range(t):
        s, t = readl()
        print(bidij.query(s-1, t-1))


if __name__ == '__main__':
    main()
