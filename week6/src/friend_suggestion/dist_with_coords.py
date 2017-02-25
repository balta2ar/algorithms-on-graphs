#!/usr/bin/python3

import sys
import queue
import math

class AStar:
    def __init__(self, n, adj, cost, x, y):
        # See the explanations of these fields in the starter for friend_suggestion
        self.n = n;
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6
        self.d = [self.inf]*n
        self.visited = [False]*n
        self.workset = []
        # Coordinates of the nodes
        self.x = x
        self.y = y

    # See the explanation of this method in the starter for friend_suggestion
    def clear(self):
        for v in self.workset:
            self.d[v] = self.inf
            self.visited[v] = False;
        del self.workset[0:len(self.workset)]

    # See the explanation of this method in the starter for friend_suggestion
    def visit(self, q, p, v, dist, measure):
        # Implement this method yourself
        pass

    # Returns the distance from s to t in the graph
    def query(self, s, t):
        self.clear()
        q = queue.PriorityQueue()
        # Implement the rest of the algorithm yourself
        return -1


def readl():
    return map(int, sys.stdin.readline().split())


def verify_dist(n, m, adj, cost, x, y):
    def dist(a, b):
        #return math.sqrt((x[a] - x[b]) ** 2 + (y[a] - y[b]) ** 2)
        return (x[a] - x[b]) ** 2 + (y[a] - y[b]) ** 2

    for node_from in range(n):
        #for node_to in adj
        neighbors = adj[node_from]
        for node_to_index, node_to in enumerate(neighbors):
            cost_in_file = cost[node_from][node_to_index] ** 2
            actual_cost = dist(node_from, node_to)
            print('coordinates: %s, %s' % ((x[node_from], y[node_from]), (x[node_to], y[node_to])))
            print('%s -> %s: in file %s, actual %s' % \
                  (node_from, node_to, cost_in_file, actual_cost))
            assert cost_in_file >= actual_cost, (node_from, node_to, cost_in_file, actual_cost)
        #print(adj[node_from])


def main():
    n,m = readl()
    x = [0 for _ in range(n)]
    y = [0 for _ in range(n)]
    adj = [[] for _ in range(n)]
    cost = [[] for _ in range(n)]
    for i in range(n):
        a, b = readl()
        x[i] = a
        y[i] = b
    for e in range(m):
        u,v,c = readl()
        adj[u-1].append(v-1)
        cost[u-1].append(c)

    verify_dist(n, m, adj, cost, x, y)
    print('DONE')
    return

    t, = readl()
    astar = AStar(n, adj, cost, x, y)
    for i in range(t):
        s, t = readl()
        print(astar.query(s-1, t-1))


if __name__ == '__main__':
    main()

