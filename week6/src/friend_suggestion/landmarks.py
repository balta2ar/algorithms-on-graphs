"""
Useful article:
http://www.redblobgames.com/pathfinding/heuristics/differential.html
http://www.redblobgames.com/pathfinding/a-star/introduction.html

Landmarks:

    1. Implement BFS to precompute Landmarks (A) to/from All distances
"""

import sys
from queue import PriorityQueue, Queue
from math import sqrt


class BreadthFirstSearchOneToAll:
    def __init__(self, n, m, adj, cost):
        self.n = n
        self.m = m
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6
        self.dist = [self.inf]*n
        #self.dist = [[self.inf]*n, [self.inf]*n]
        self.parent = [[None]*n, [None]*n]      # Used for backtracking

    def clear(self):
        self.dist = [self.inf]*self.n
        #self.dist = #[[self.inf]*self.n, [self.inf]*self.n]

    def query(self, source, target):
        self.clear()

        #visited = set()
        queue = Queue()

        self.dist[source] = 0
        #visited.add(source)
        queue.put(source)

        while not queue.empty():
            u = queue.get()
            neighbors = self.adj[0][u]
            for v_index, v in enumerate(neighbors):
                alt = self.dist[u] + self.cost[0][u][v_index]
                if alt < self.dist[v]:
                    self.dist[v] = alt
                    queue.put(v)
                #if v not in visited:
                #    visited.add(v)

        if self.dist[target] != self.inf:
            return self.dist[target]
        return -1


class LandmarksAStarOnedirectional:
    def __init__(self, n, m, adj, cost, x, y):
        # See the explanations of these fields in the starter for friend_suggestion
        self.n = n
        self.m = m
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6
        self.dist = [[self.inf]*n, [self.inf]*n]
        self.visited = [False]*n
        self.workset = []
        self.parent = [[None]*n, [None]*n]      # Used for backtracking
        # Coordinates of the nodes
        self.x = x
        self.y = y

    # See the explanation of this method in the starter for friend_suggestion
    def clear(self):
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
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
            self.visit(queue, u, source, target)

            if self.dist[0][target] != self.inf:
                return self.backtrack(source, target)

        return -1

    def p(self, u, source, target):
        dist_u_target = (self.x[u] - self.x[target]) ** 2 + (self.y[u] - self.y[target]) ** 2
        return sqrt(dist_u_target)

    def visit(self, queue, u, source, target):
        """
        Try to relax the distance to node u from direction side by value dist.
        """
        local_adj = self.adj
        local_cost = self.cost
        local_dist = self.dist
        #local_parent = self.parent
        local_workset = self.workset
        #local_x = self.x
        #local_y = self.y

        neighbors = local_adj[0][u]
        for v_index, v in enumerate(neighbors):
            print(v, file=sys.stderr)
            potential = -self.p(u, source, target) + self.p(v, source, target)
            edge_weight = local_cost[0][u][v_index] + potential

            alt = local_dist[0][u] + edge_weight

            if alt < local_dist[0][v]:
                local_dist[0][v] = alt
                #local_parent[0][v] = u
                queue[0].put((alt, v))
                #local_workset.append(v)

        self.visited[u] = True
        local_workset.append(u)

    def backtrack(self, source, target):
        # path = []

        # current = target
        # while current != source:
        #     path.append(current)
        #     current = self.parent[0][current]
        # path.append(current)

        u = source
        v = target

        potential = -self.p(u, source, target) + self.p(v, source, target)

        #print(list(reversed(path)))
        #return int(round(self.dist[0][target] - potential))
        return int(round(self.dist[0][target] - potential))


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

    # adj = [[] for _ in range(n)]
    # cost = [[] for _ in range(n)]
    # for _ in range(m):
    #     u, v, c = readl()
    #     adj[u-1].append(v-1)
    #     cost[u-1].append(c)

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
    #n, m, adj, cost, x, y = read_from_stdin_straight()
    n, m, adj, cost, x, y = read_from_stdin_reversed()
    #verify_dist(n, m, adj, cost, x, y)
    #print('DONE')
    #returread_from_stdin_straight

    t, = readl()

    alg = 'abi'
    if len(sys.argv) > 1:
        alg = sys.argv[1]

    if alg == 'laone':
        astar = LandmarksAStarOnedirectional(n, m, adj, cost, x, y)
    elif alg == 'bfs':
        astar = BreadthFirstSearchOneToAll(n, m, adj, cost)
    # elif alg == 'abi':
    #     astar = AStarBidirectional(n, m, adj, cost, x, y)
    else:
        print('Unknown algorithm: %s' % alg)

    #astar = AStar(n, adj, cost, x, y)
    #astar = AStarBidirectional(n, m, adj, cost, x, y)
    #astar = AStarOnedirectional(n, m, adj, cost, x, y)
    for _ in range(t):
        s, t = readl()
        print(astar.query(s-1, t-1))


if __name__ == '__main__':
    main()
