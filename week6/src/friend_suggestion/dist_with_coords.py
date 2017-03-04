#!/usr/bin/python3

import sys
from queue import PriorityQueue
from math import sqrt


# -----------------------------------------------------------------------------


class AStarOnedirectional:
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
            #self.parent[0][v] = self.parent[1][v] = None
        #del self.workset[0:len(self.workset)]
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

    # def get_dist(self, u, v):
    #     return (self.x[u] - self.x[v]) ** 2 + (self.y[u] - self.y[v]) ** 2
    #
    # def potential(self, u, v, source, target):
    #     return -self.get_dist(u, target) + self.get_dist(v, target)
    #
    # def get_edge_weight(self, u, v, v_index, source, target):
    #     return self.cost[0][u][v_index] + self.potential(u, v, source, target)

    def visit(self, queue, u, source, target):
        """
        Try to relax the distance to node u from direction side by value dist.
        """
        local_adj = self.adj
        local_cost = self.cost
        local_dist = self.dist
        local_parent = self.parent
        local_workset = self.workset
        local_x = self.x
        local_y = self.y

        #neighbors = self.adj[0][u]
        neighbors = local_adj[0][u]
        for v_index, v in enumerate(neighbors):
            #alt = self.dist[0][u] + self.cost[0][u][v_index]
            #alt = self.dist[0][u] + self.potential(u, source, target)

            #return (self.x[u] - self.x[v]) ** 2 + (self.y[u] - self.y[v]) ** 2

            #return -self.get_dist(u, target) + self.get_dist(v, target)
            # edge_weight
            #return self.cost[0][u][v_index] + self.potential(u, v, source, target)
            dist_u_target = (local_x[u] - local_x[target]) ** 2 + (local_y[u] - local_y[target]) ** 2
            dist_v_target = (local_x[v] - local_x[target]) ** 2 + (local_y[v] - local_y[target]) ** 2
            potential = -sqrt(dist_u_target) + sqrt(dist_v_target)
            edge_weight = local_cost[0][u][v_index] + potential


            alt = local_dist[0][u] + edge_weight
            #alt = local_dist[0][u] + self.get_edge_weight(u, v, v_index, source, target)

            if alt < local_dist[0][v]:
                local_dist[0][v] = alt
                local_parent[0][v] = u
                queue[0].put((alt, v))
                #local_workset.append(v)
                #print('> %s' % v)
                #self.workset.append(u)

        self.visited[u] = True
        local_workset.append(u)
        #self.workset.append(u)

    def backtrack(self, source, target):
        path = []

        current = target
        while current != source:
            path.append(current)
            current = self.parent[0][current]
        path.append(current)

        dist_source_target = (self.x[source] - self.x[target]) ** 2 + (self.y[source] - self.y[target]) ** 2
        #dist_target_target = (self.x[target] - self.x[target]) ** 2 + (self.y[target] - self.y[target]) ** 2
        potential = -sqrt(dist_source_target) #+ dist_target_target

        #print(list(reversed(path)))
        #jreturn self.dist[0][target] - self.potential(source, target, source, target)
        return int(round(self.dist[0][target] - potential))


# -----------------------------------------------------------------------------


class AStarBidirectional:
    def __init__(self, n, m, adj, cost, x, y):
        self.n = n                              # Number of nodes
        self.m = m
        self.adj = adj
        self.cost = cost
        self.x = x
        self.y = y
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        #self.visited = [False]*n                  # visited[v] == True iff v was visited by forward or backward search
        self.visited = [[False]*n, [False]*n]      # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search
        self.parent = [[None]*n, [None]*n]      # Used for backtracking
        #self.best_path_len = self.inf

    def clear(self):
        """Reinitialize the data structures for the next query after the previous query."""
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            #self.parent[0][v] = self.parent[1][v] = None
            self.visited[0][v] = self.visited[1][v] = False
        #del self.workset[0:len(self.workset)]
        self.workset = []
        #self.best_path_len = self.inf

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

        # if self.best_path_len < self.inf:
        #     return self.get_shortest_path(source, target)

        return -1

    def do_iteration(self, queue, side, source, target):
        # u = self.get_min(queue, side)
        # if u is None:
        #     return None
        if queue[side].empty():
            return None
        _, u = queue[side].get()

        self.visit(queue, side, u, source, target)

        # if self.can_stop(side, u):
        other_side = 1 - side
        if self.visited[other_side][u]:
            return self.get_shortest_path(side, source, target)

        return None

    def p(self, side, u, source, target):
        dist_u_target = (self.x[u] - self.x[target]) ** 2 + (self.y[u] - self.y[target]) ** 2
        dist_source_u = (self.x[source] - self.x[u]) ** 2 + (self.y[source] - self.y[u]) ** 2

        pi_f = sqrt(dist_u_target)
        pi_r = sqrt(dist_source_u)

        result = (pi_f - pi_r) / 2.
        result *= (1 - side) + -1 * (side) # equivalent of 1. if side == 0 else -1.
        return result

    def visit(self, queue, side, u, source, target):
        local_adj = self.adj
        local_cost = self.cost
        local_dist = self.dist
        local_parent = self.parent
        local_workset = self.workset
        local_x = self.x
        local_y = self.y

        other_side = 1 - side
        neighbors = local_adj[side][u]

        for v_index, v in enumerate(neighbors):
            # dist_u_target = (local_x[u] - local_x[target]) ** 2 + (local_y[u] - local_y[target]) ** 2
            # dist_u_source = (local_x[u] - local_x[source]) ** 2 + (local_y[u] - local_y[source]) ** 2
            # dist_v_target = (local_x[v] - local_x[target]) ** 2 + (local_y[v] - local_y[target]) ** 2
            # dist_v_source = (local_x[v] - local_x[source]) ** 2 + (local_y[v] - local_y[source]) ** 2
            #
            # pi_f_u = sqrt(dist_u_target)
            # pi_r_u = sqrt(dist_u_source)
            # pi_f_v = sqrt(dist_v_target)
            # pi_r_v = sqrt(dist_v_source)
            #
            # p_f_u = (pi_f_u - pi_r_u) / 2.
            # p_r_u = -p_f_u
            # p_f_v = (pi_f_v - pi_r_v) / 2.
            # p_r_v = -p_f_v

            # dist_u_target = (local_x[u] - local_x[target]) ** 2 + (local_y[u] - local_y[target]) ** 2
            # dist_v_target = (local_x[v] - local_x[target]) ** 2 + (local_y[v] - local_y[target]) ** 2
            # potential = -sqrt(dist_u_target) + sqrt(dist_v_target)
            # edge_weight = local_cost[side][u][v_index] + potential
            #potential = -p_f_u + p_f_v if side == 0 else -p_r_v + p_r_u

            # if side == 0:
            #     potential = -self.p(side, u, source, target) + self.p(side, v, source, target)
            # else:
            #     potential = -self.p(other_side, v, source, target) + self.p(other_side, u, source, target)
            potential = -self.p(side, u, source, target) + self.p(side, v, source, target)

            edge_weight = local_cost[side][u][v_index] + potential

            alt = local_dist[side][u] + edge_weight
            #alt = local_dist[side][u] + local_cost[side][u][v_index]

            if alt < local_dist[side][v]:
                local_dist[side][v] = alt
                local_parent[side][v] = u
                queue[side].put((alt, v))
                local_workset.append(v)
                #print('> %s' % v)

            # # update self.best_path_len (mu) if necessary
            # other_side = 1 - side
            # if self.dist[other_side][v] < self.inf:
            #     new_best_path_len = self.cost[side][u][v_index] + \
            #         self.dist[side][u] + self.dist[other_side][v]
            #
            #     if new_best_path_len < self.best_path_len:
            #         self.best_path_len = new_best_path_len

        self.visited[side][u] = True
        local_workset.append(u)

    # def can_stop(self, side, u):
    #     other_side = 1 - side
    #     return self.visited[other_side][u]

    # def get_min(self, queue, side):
    #     if queue[side].empty():
    #         return None
    #     _, u = queue[side].get()
    #     return u

    def get_shortest_path(self, side, source, target):
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

        # dist_source_target = (self.x[source] - self.x[target]) ** 2 + (self.y[source] - self.y[target]) ** 2
        #dist_target_target = (self.x[target] - self.x[target]) ** 2 + (self.y[target] - self.y[target]) ** 2
        # potential = -sqrt(dist_source_target) #+ dist_target_target

        #print(list(reversed(path)))
        #jreturn self.dist[0][target] - self.potential(source, target, source, target)
        #return int(round(self.dist[0][target] - potential))
        other_side = 1 - side

        u = source
        v = target

        print('side', side)

        # if side == 0:
        #     potential = -self.p(side, v, source, target) + self.p(side, u, source, target)
        # else:
        #     potential = -self.p(other_side, v, source, target) + self.p(other_side, u, source, target)
        potential = -self.p(side, u, source, target) + self.p(side, v, source, target)
        potential *= (1 - side) + -1 * (side) # equivalent of 1. if side == 0 else -1.

        # dist_u_target = (self.x[u] - self.x[target]) ** 2 + (self.y[u] - self.y[target]) ** 2
        # dist_u_source = (self.x[u] - self.x[source]) ** 2 + (self.y[u] - self.y[source]) ** 2
        # dist_v_target = (self.x[v] - self.x[target]) ** 2 + (self.y[v] - self.y[target]) ** 2
        # dist_v_source = (self.x[v] - self.x[source]) ** 2 + (self.y[v] - self.y[source]) ** 2
        #
        # pi_f_u = sqrt(dist_u_target)
        # pi_r_u = sqrt(dist_u_source)
        # pi_f_v = sqrt(dist_v_target)
        # pi_r_v = sqrt(dist_v_source)
        #
        # p_f_u = (pi_f_u - pi_r_u) / 2.
        # p_r_u = -p_f_u
        # p_f_v = (pi_f_v - pi_r_v) / 2.
        # p_r_v = -p_f_v
        #
        # potential = -p_f_u + p_f_v if side == 0 else -p_r_v + p_r_u

        # dist_u_target = (local_x[u] - local_x[target]) ** 2 + (local_y[u] - local_y[target]) ** 2
        # dist_v_target = (local_x[v] - local_x[target]) ** 2 + (local_y[v] - local_y[target]) ** 2
        # potential = -sqrt(dist_u_target) + sqrt(dist_v_target)
        # edge_weight = local_cost[side][u][v_index] + potential

        return int(round(dist - potential))


# -----------------------------------------------------------------------------


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


def read_from_stdin_straight():
    n, m = readl()
    x = [0 for _ in range(n)]
    y = [0 for _ in range(n)]
    adj = [[] for _ in range(n)]
    cost = [[] for _ in range(n)]
    for i in range(n):
        a, b = readl()
        x[i] = a
        y[i] = b
    for _ in range(m):
        u, v, c = readl()
        adj[u-1].append(v-1)
        cost[u-1].append(c)
    return n, m, adj, cost, x, y


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

    if alg == 'aone':
        astar = AStarOnedirectional(n, m, adj, cost, x, y)
    elif alg == 'abi':
        astar = AStarBidirectional(n, m, adj, cost, x, y)
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
