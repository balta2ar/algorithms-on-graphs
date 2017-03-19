#!/usr/bin/python3


import sys
import pickle
from queue import PriorityQueue
from collections import deque
from itertools import product
#from collections import namedtuple
import logging


FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.ERROR)
_logger = logging.getLogger(__name__)


# Maximum allowed edge length
MAXLEN = 2 * 10**6


class _DijkstraOnedirectionalWitnessSearch:
    def __init__(self, n, m, adj, cost, contracted, _x=None, _y=None):
        self.n = n                              # Number of nodes
        self.m = m
        self.adj = adj
        self.cost = cost
        self.inf = MAXLEN                        # All distances in the graph are smaller
        self.dist = [self.inf]*n                 # Initialize distances for forward and backward searches
        #self.visited = [False]*n                 # visited[v] == True iff v was visited by forward or backward search
        self.workset = []                        # All the nodes visited by forward or backward search
        self.parent = [None]*n
        # These vertices are coming from parent class. After a vertice
        # is contracted, Dijkstra should ignore it in the search.
        self.contracted = contracted

    def clear(self):
        """
        Reinitialize the data structures for the next query after the previous query.
        """
        for v in self.workset:
            self.dist[v] = self.inf
            #self.dist[v] = self.dist[v] = self.inf
            #self.visited[v] = False
        self.workset = []

    def query(self, source, target, ignored_node, max_cost):
        """
        If target == -1, then search until stopped by other criterions
        or until run out of unvisited nodes.
        """
        if source == target:
            return 0

        self.clear()
        queue = PriorityQueue()

        self.dist[source] = 0
        queue.put((0, source))
        self.parent[source] = None

        while not queue.empty():
            _, u = queue.get()
            if u != ignored_node and not self.contracted[u]:
                self.visit(queue, u, ignored_node, max_cost)

        if target != -1 and self.dist[target] != self.inf:
            #return self.backtrack(source, target)
            return self.dist[target]

        return -1

    def visit(self, queue, u, ignored_node, max_cost):
        """
        Try to relax the distance to node u from direction side by value dist.
        """
        neighbors = self.adj[0][u]
        for v_index, v in enumerate(neighbors):
            if v == ignored_node or self.contracted[v]:
                continue

            alt = self.dist[u] + self.cost[0][u][v_index]

            if alt < self.dist[v] and alt <= max_cost:
                self.dist[v] = alt
                queue.put((alt, v))
                self.workset.append(v)
                self.parent[v] = u

        #self.visited[u] = True
        self.workset.append(u)

    def backtrack(self, source, target):
        path = []

        current = target
        while current != source:
            path.append(current)
            current = self.parent[current]
        path.append(current)

        #print('witness path', list(reversed(path)))
        #return self.dist[target]
        return list(reversed(path))


#Shortcut = namedtuple('Shortcut', 'u v w cost')


class DistPreprocessSmall:
    CACHE_FILENAME = 'untracked/astar/ch.pkl.cache'

    def __init__(self, n, m, adj, cost, _x=None, _y=None):
        # See description of these parameters in the starter for friend_suggestion
        self.n = n
        self.m = m
        self.inf = n * MAXLEN
        self.adj = adj
        self.cost = cost
        self.dist = [[self.inf] * n, [self.inf] * n]
        self.visited = [[False]*n, [False]*n]
        self.workset = []
        self.parent = [[None]*n, [None]*n]       # Used for backtracking
        self.shortcuts = dict() # []
        #self.queue = [PriorityQueue(), PriorityQueue()]
        # Levels of nodes for node ordering heuristics
        self.level = [0] * n
        # Positions of nodes in the node ordering
        #self.rank = [0] * n
        self.rank = []
        self.counter = 0

        self.estimate = None

        # Implement preprocessing here
        self.witness_searcher = _DijkstraOnedirectionalWitnessSearch(
            n, m, adj, cost, self.visited[0])

        self.preprocess()

        # cached_cost = self.load_cache()
        # if cached_cost is None:
        #     #self.cost = self.pre
        #     self.preprocess()
        #     self.save_cache(self.cost)
        # else:
        #     self.cost = cached_cost

    def save_to_file(self, filename):
        with open(filename, 'w') as file_:
            m = self.m + len(self.shortcuts)
            file_.write('%s %s\n' % (self.n, m))
            for u, vs in enumerate(self.adj[0]):
                for v_index, v in enumerate(vs):
                    file_.write('%s %s %s\n' % (u+1, v+1, self.cost[0][u][v_index]))
            file_.write('0\n') # no queries
            file_.write('%s\n' % len(self.shortcuts))
            for u, v in self.shortcuts:
                file_.write('%s %s\n' % (u+1, v+1))

    def load_cache(self):
        try:
            costs = []
            with open(DistPreprocessSmall.CACHE_FILENAME, 'rb') as cache_:
                costs = pickle.load(cache_)
                # for line in cache_:
                #     landmark = [int(x) for x in line.strip().split()]
                #     costs.append(landmark)
            _logger.info('Loaded CH edges from %s', DistPreprocessSmall.CACHE_FILENAME)
            return costs
        except IOError:
            return None

    def save_cache(self, obj):
        with open(DistPreprocessSmall.CACHE_FILENAME, 'wb') as cache_:
            pickle.dump(obj, cache_, pickle.HIGHEST_PROTOCOL)
            # for landmark in self.costs:
            #     line = ' '.join(map(str, landmark))
            #     cache_.write('%s\n' % line)

    # --- PREPROCESSING PART --------------------------------------------------

    def preprocess(self):
        """
        1. Eliminate nodes one by one in some order.
        2. Add shortcuts to preserve distances.

        Output: augmented graph + node order.
        """
        #self.save_to_file('ch-steps1/contracted-step%s.in' % 0)
        for u in range(self.n):
            _logger.info('contract %s', u)
            self.contract(u)
            #self.save_to_file('ch-steps1/contracted-step%s.in' % (u+1))
            #self.save_to_file('untracked/contracted-step%s.in' % u)

        #from pprint import pformat
        #_logger.info('shortcuts: %s', pformat(self.shortcuts))
        _logger.info('# shortcuts: %s', len(self.shortcuts))

    def contract(self, node):
        # outgoing_nodes = self.adj[0][node]
        # incoming_nodes = self.adj[1][node]

        # 3. Try to find witness path
        #    Witness search: run one directional Dijkstra from each predecessor
        #    (no target, limit max cost, limit number of hops)

        # This bound may be too relaxed.
        #max_witness_path_cost = self.get_max_witness_path_cost(node)
        new_shortcuts = dict()

        for (u_index, u), (w_index, w) in self.iter_candidates(node):

            # This is maximum for one pair of (u, v), (v, w). It's a very strict
            # bound.
            # max_witness_path_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]

            # Current incoming + max of all outgoing edges.
            max_witness_path_cost = self.cost[1][node][u_index] + max(self.cost[0][node])

            _logger.info('doing witness search (%s,%s) max=%s', u, w, max_witness_path_cost)
            witness_path_cost = self.witness_searcher.query(u, w, node, max_witness_path_cost)
            if witness_path_cost == -1:
                u_w_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
                _logger.info('saving arc to buffer (%s,%s) = %s, max=%s', u, w, u_w_cost, max_witness_path_cost)

                new_shortcuts[(u, w)] = (node, u_w_cost)
                # self.add_arc(u, w, u_w_cost)
                # self.shortcuts[(u, w)] = (node, u_w_cost)

                #self.shortcuts.append(Shortcut(u, node, w, u_w_cost))
            else:
                witness_path = self.witness_searcher.backtrack(u, w)
                _logger.info('found witness path %s of cost %s for (%s,%s), max=%s',
                             witness_path, witness_path_cost, u, w, max_witness_path_cost)
                #pass

        for (u, w), (v, u_w_cost) in new_shortcuts.items():
            _logger.info('actually adding arc (%s,%s v %s) = %s, max=%s', u, w, v, u_w_cost, max_witness_path_cost)
            self.add_arc(u, w, u_w_cost)
            self.shortcuts[(u, w)] = (v, u_w_cost)

        self.mark_visited(node)
        self.rank.append(node)
        self.level[node] = self.counter
        self.counter += 1

    # def find_witness_path(self, u, w, v, max_cost):
    #     pass

    def iter_candidates(self, v):
        outgoing_nodes = self.adj[0][v]
        incoming_nodes = self.adj[1][v]
        for (u_index, u), (w_index, w) in product(enumerate(incoming_nodes),
                                                  enumerate(outgoing_nodes)):
            # TODO u != w???
            if u != w and not self.visited[0][u] and not self.visited[0][w]:
                yield (u_index, u), (w_index, w)

    def get_max_witness_path_cost(self, node):
        # outgoing_nodes = self.adj[0][node]
        # incoming_nodes = self.adj[1][node]

        # 1. Find max sum of all segments (incoming + outgoing edges)
        # for (u_index, u), (w_index, w) in product(enumerate(incoming_nodes),
        #                                           enumerate(outgoing_nodes)):
        max_u_w_cost = 0
        for (u_index, _u), (w_index, w) in self.iter_candidates(node):
            u_w_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
            max_u_w_cost = max(max_u_w_cost, u_w_cost)

        # for (u_index, u), (w_index, w) in product(enumerate(incoming_nodes),
        #                                           enumerate(outgoing_nodes)):
        #     u_w_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
        # 2. Find min w' -> w cost
        min_w_prime_w_cost = self.inf
        for w in self.adj[0][node]:
            for w_prime_index, w_prime in enumerate(self.adj[1][w]):
                if not self.visited[0][w] and not self.visited[0][w_prime]:
                    # TODO: min or max???
                    min_w_prime_w_cost = min(min_w_prime_w_cost,
                                             self.cost[1][w][w_prime_index])

        #max_witness_path_cost = max_u_w_cost - min_w_prime_w_cost
        max_witness_path_cost = max_u_w_cost
        return max_witness_path_cost

    def mark_visited(self, x):
        if not self.visited[0][x]:
            self.visited[0][x] = True
            self.workset.append(x)

    def add_arc(self, u, v, c):
        """
        Return true if new edge has been added. False if an existing edge has
        been updated.
        """
        def update(adj, cost, u, v, c):
            for i in range(len(adj[u])):
                if adj[u][i] == v:
                    cost[u][i] = min(cost[u][i], c)
                    return True
            adj[u].append(v)
            cost[u].append(c)

        a = update(self.adj[0], self.cost[0], u, v, c)
        b = update(self.adj[1], self.cost[1], v, u, c)
        return a or b

    # Makes shortcuts for contracting node v
    def shortcut(self, v):
        # Implement this method yourself

        # Compute the node importance in the end
        shortcut_count = 0
        neighbors = 0
        shortcut_cover = 0
        level = 0
        # Compute correctly the values for the above heuristics before computing the node importance
        importance = (shortcut_count - len(self.adj[0][v]) - len(self.adj[1][v])) + neighbors + shortcut_cover + level
        return importance, shortcut_count, level

    # --- QUERY PART ----------------------------------------------------------

    def clear(self):
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            self.visited[0][v] = self.visited[1][v] = False
        self.workset = []
        #del self.workset[:]
        #self.visited = [False] * self.n

    def query(self, source, target):
        _logger.info('query %s -> %s', source, target)
        if source == target:
            return 0

        self.clear()
        queue = [PriorityQueue(), PriorityQueue()]

        self.dist[0][source] = self.dist[1][target] = 0
        queue[0].put((0, source))
        queue[1].put((0, target))

        self.estimate = self.inf
        while not queue[0].empty() or not queue[1].empty():
            self.do_iteration(queue, 0)
            self.do_iteration(queue, 1)

        result = -1 if self.estimate == self.inf else self.estimate
        _logger.info('query %s -> %s result %s', source, target, result)
        if result != -1:
            self.backtrack(source, target)
        return result

    def do_iteration(self, queue, side):
        if queue[side].empty():
            return None
        _, u = queue[side].get()

        if self.dist[side][u] <= self.estimate:
            self.visit(queue, side, u)

        other_side = 1 - side
        if self.visited[other_side][u]:
            alt = self.dist[0][u] + self.dist[1][u]
            if alt < self.estimate:
                self.estimate = alt
            #return self.backtrack(source, target)

        return None

    def visit(self, queue, side, u):
        _logger.info('visit %s, side %s', u, side)
        local_adj = self.adj
        local_dist = self.dist
        local_cost = self.cost
        local_workset = self.workset
        local_level = self.level
        local_parent = self.parent

        neighbors = local_adj[side][u]

        for v_index, v in enumerate(neighbors):
            #print(v, file=sys.stderr)

            # Consider only edges going up
            if local_level[u] >= local_level[v]:
                _logger.info('skipping due to level(%s) %s >= level(%s) %s',
                             u, local_level[u], v, local_level[v])
                continue

            alt = local_dist[side][u] + local_cost[side][u][v_index]
            _logger.info('alt u v %s %s = %s', u, v, alt)

            if alt < local_dist[side][v]:
                _logger.info('new alt %s for u v %s %s side %s', alt, u, v, side)
                local_dist[side][v] = alt
                local_parent[side][v] = u
                queue[side].put((alt, v))
                local_workset.append(v)
                self.parent[side][v] = u

        self.visited[side][u] = True
        local_workset.append(u)

    def _human_path(self, path):
        return ' '.join(map(lambda x: str(x+1), path))

    def backtrack(self, source, target):
        #print('backtrack', source, target)
        # path = []
        #
        # current = target
        # while current != source:
        #     path.append(current)
        #     current = self.parent[0][current]
        # path.append(current)
        #
        # #print(list(reversed(path)))
        # print(' '.join(map(lambda x: str(x+1), reversed(path))))
        # return self.dist[0][target]

        dist = self.inf
        u_best = -1

        for u in self.workset:
            candidate_dist = self.dist[0][u] + self.dist[1][u]
            if candidate_dist < dist:
                u_best = u
                dist = candidate_dist

        path = []
        last = u_best

        while last != source:
            path.append(last)
            last = self.parent[0][last]
        path.append(last)
        path.reverse()
        _logger.info('path first part HUMAN %s', self._human_path(path))

        last = u_best
        while last != target:
            last = self.parent[1][last]
            path.append(last)
        _logger.info('path first+last part HUMAN %s', self._human_path(path))

        path = self.expand_shortcuts(path)
        #print(' '.join(map(lambda x: str(x+1), path)))
        _logger.info('result path HUMAN %s', self._human_path(path))
        return dist, path

    def expand_shortcuts(self, path):
        # print('path before expansion', self._human_path(path))
        if len(path) == 1:
            return path

        result = []
        queue = deque(path)

        while len(queue) > 1:
            u, w = queue.popleft(), queue.popleft()
            if (u, w) in self.shortcuts:
                v, _cost = self.shortcuts[(u, w)]
                # print('expanded %s %s %s = %s' % (u, v, w, _cost))
                queue.appendleft(w)
                queue.appendleft(v)
                queue.appendleft(u)
                # print('queue', queue)
            else:
                # print('not a shortcut %s %s' % (u, w))
                result.append(u)
                queue.appendleft(w)
                # print('queue', queue)
                # print('result', result)
        result.append(queue.popleft())

        # print('path after expansion', self._human_path(result))
        return result


def readl():
    return map(int, sys.stdin.readline().split())


def main():
    n, m = readl()
    adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
    cost = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for _ in range(m):
        u, v, c = readl()
        adj[0][u-1].append(v-1)
        cost[0][u-1].append(c)
        adj[1][v-1].append(u-1)
        cost[1][v-1].append(c)

    ch = DistPreprocessSmall(n, m, adj, cost)
    print("Ready")
    sys.stdout.flush()
    ch.save_to_file('untracked/contracted.in')

    t, = readl()
    for _ in range(t):
        s, t = readl()
        print(ch.query(s-1, t-1))


if __name__ == '__main__':
    main()
