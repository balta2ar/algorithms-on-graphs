"""
Useful article:
http://www.redblobgames.com/pathfinding/heuristics/differential.html
http://www.redblobgames.com/pathfinding/a-star/introduction.html

Landmarks:

    1. Implement BFS to precompute Landmarks (A) to/from All distances

Notes:

function distance_heuristic(a, z) {
    return Math.abs(a.x - z.x) + Math.abs(a.y - z.y);
}

function landmark_heuristic(a, z) {
    return Math.max(distance_heuristic(a, z), L_cost[z] - L_cost[a]);
}

function landmark_heuristic(a, z) {
    return Math.max(distance_heuristic(a, z), Math.abs(L_cost[z] - L_cost[a]));
}

function landmark_heuristic(a, z) {
    // Assume landmarks are in array L_costs[]
    var d = distance_heuristic(a, z);
    for (var i = 0; i < L_costs.length; i++) {
        d = Math.max(d, L_costs[i][z] - L_costs[i][a]);
    }
    return d;
}
"""

import sys
from queue import PriorityQueue, Queue
from math import sqrt
#from copy import copy
import pickle


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

        if target is not None:
            if self.dist[target] != self.inf:
                return self.dist[target]
        return -1


class LandmarksHeuristic:
    CACHE_FILENAME = 'untracked/astar/landmarks.pkl.cache'

    def __init__(self, n, m, adj, cost, nodes):
        self.costs = self.load_cache()
        if self.costs is None:
            self.costs = self.preprocess(n, m, adj, cost, nodes)
        self.save_cache(self.costs)

    def preprocess(self, n, m, adj, cost, nodes):
        costs = []
        bfs = BreadthFirstSearchOneToAll(n, m, adj, cost)
        for _, node in enumerate(nodes):
            #print('Processing landmark %s/%s' % (i+1, len(nodes)))
            print('.', end='', flush=True)
            bfs.query(node, None)
            costs.append(bfs.dist[:])
        print()
        return costs

    def dist(self, u, v, initial_cost):
        cost = initial_cost
        for landmark in self.costs:
            cost = max(cost, landmark[v] - landmark[u])
            cost = max(cost, landmark[u] - landmark[v])
        return cost

    def load_cache(self):
        try:
            costs = []
            with open(LandmarksHeuristic.CACHE_FILENAME, 'rb') as cache_:
                costs = pickle.load(cache_)
                # for line in cache_:
                #     landmark = [int(x) for x in line.strip().split()]
                #     costs.append(landmark)
            print('Loaded landmarks from %s' % LandmarksHeuristic.CACHE_FILENAME)
            return costs
        except IOError:
            return None

    def save_cache(self, obj):
        with open(LandmarksHeuristic.CACHE_FILENAME, 'wb') as cache_:
            pickle.dump(obj, cache_, pickle.HIGHEST_PROTOCOL)
            # for landmark in self.costs:
            #     line = ' '.join(map(str, landmark))
            #     cache_.write('%s\n' % line)



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
        self.x = x
        self.y = y

        nodes = self.read_landmark_nodes()
        print('Preprocessing landmarks', nodes)
        self.landmarks = LandmarksHeuristic(n, m, adj, cost, nodes)
        print('Preprocessed %s landmarks' % len(nodes))

    def read_landmark_nodes(self):
        #with open('untracked/astar/landmarks.usa-road.10k.txt') as file_:
        with open('untracked/astar/landmarks.usa-road.txt') as file_:
            nodes = list(map(int, file_.readlines()))
            # count = int(file_.readline().strip())
            # for _ in range(count):
            #     nodes = [int(x) for x in file_.readline().strip().split()]
        return nodes

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
        potential = sqrt(dist_u_target)
        potential = self.landmarks.dist(u, target, potential)
        return potential

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
            #print(v, file=sys.stderr)
            potential = -self.p(u, source, target) + self.p(v, source, target)
            edge_weight = local_cost[0][u][v_index] + potential

            alt = local_dist[0][u] + edge_weight

            if alt < local_dist[0][v]:
                local_dist[0][v] = alt
                #local_parent[0][v] = u
                queue[0].put((alt, v))
                local_workset.append(v)

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


class LandmarksAStarBidirectional:
    def __init__(self, n, m, adj, cost, x, y):
        self.n = n                              # Number of nodes
        self.m = m
        self.adj = adj
        self.cost = cost
        self.inf = n*10**6                      # All distances in the graph are smaller
        self.dist = [[self.inf]*n, [self.inf]*n]   # Initialize distances for forward and backward searches
        self.visited = [[False]*n, [False]*n]      # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                       # All the nodes visited by forward or backward search
        self.parent = [[None]*n, [None]*n]      # Used for backtracking
        self.x = x
        self.y = y

        nodes = self.read_landmark_nodes()
        print('Preprocessing landmarks', nodes)
        self.landmarks = LandmarksHeuristic(n, m, adj, cost, nodes)
        print('Preprocessed %s landmarks' % len(nodes))

    def read_landmark_nodes(self):
        #with open('untracked/astar/landmarks.usa-road.10k.txt') as file_:
        with open('untracked/astar/landmarks.usa-road.txt') as file_:
            nodes = list(map(int, file_.readlines()))
            # count = int(file_.readline().strip())
            # for _ in range(count):
            #     nodes = [int(x) for x in file_.readline().strip().split()]
        return nodes

    def clear(self):
        """Reinitialize the data structures for the next query after the previous query."""
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            #self.parent[0][v] = self.parent[1][v] = None
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

        self.visit(queue, side, u, source, target)

        other_side = 1 - side
        if self.visited[other_side][u]:
            return self.get_shortest_path(side, source, target)

        return None

    def p(self, side, u, source, target):
        dist_u_target = (self.x[u] - self.x[target]) ** 2 + (self.y[u] - self.y[target]) ** 2
        dist_source_u = (self.x[source] - self.x[u]) ** 2 + (self.y[source] - self.y[u]) ** 2

        pi_f = sqrt(dist_u_target)
        pi_r = sqrt(dist_source_u)

        pi_f = self.landmarks.dist(u, target, pi_f)
        pi_r = self.landmarks.dist(source, u, pi_r)

        result = (pi_f - pi_r) / 2.
        result *= (1 - side) + -1 * side # equivalent of 1. if side == 0 else -1.
        return result

    def visit(self, queue, side, u, source, target):
        local_adj = self.adj
        local_cost = self.cost
        local_dist = self.dist
        local_parent = self.parent
        local_workset = self.workset
        # local_x = self.x
        # local_y = self.y

        neighbors = local_adj[side][u]

        for v_index, v in enumerate(neighbors):
            print(v, file=sys.stderr)
            potential = -self.p(side, u, source, target) + self.p(side, v, source, target)
            edge_weight = local_cost[side][u][v_index] + potential
            alt = local_dist[side][u] + edge_weight

            if alt < local_dist[side][v]:
                local_dist[side][v] = alt
                local_parent[side][v] = u
                queue[side].put((alt, v))
                local_workset.append(v)

        self.visited[side][u] = True
        local_workset.append(u)

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

        u = source
        v = target

        potential = -self.p(side, u, source, target) + self.p(side, v, source, target)
        potential *= (1 - side) + -1 * side # equivalent of 1. if side == 0 else -1.

        return int(round(dist - potential))



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
    elif alg == 'ladi':
        astar = LandmarksAStarBidirectional(n, m, adj, cost, x, y)
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
