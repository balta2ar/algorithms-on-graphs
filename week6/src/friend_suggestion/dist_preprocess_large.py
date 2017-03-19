#!/usr/bin/python3


import sys
import pickle
#from queue import PriorityQueue
from heapq import heappush, heappop
from collections import deque
from itertools import product
#from collections import namedtuple
import logging


FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)
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

    def get_dist(self, target):
        return -1 if self.dist[target] == self.inf else self.dist[target]

    def query(self, source, target, ignored_node, max_cost, max_hops):
        """
        If target == -1, then search until stopped by other criterions
        or until run out of unvisited nodes.
        """
        if source == target:
            return 0

        # if source == 8:
        #     from ipdb import set_trace; set_trace()

        self.clear()
        queue = [] # PriorityQueue()

        self.dist[source] = 0
        #queue.put((0, source))
        heappush(queue, (0, source))
        self.parent[source] = None
        self.workset.append(source)
        visit_count = 0

        while queue and visit_count < max_hops:
            _, u = heappop(queue)
            if u != ignored_node and not self.contracted[u]:
                self.visit(queue, u, ignored_node, max_cost)
                visit_count += 1

        # _logger.info('WITNESS VISITS %s', visit_count)

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
                heappush(queue, (alt, v))
                self.workset.append(v)
                self.parent[v] = u

        #self.visited[u] = True
        self.workset.append(u)

    def backtrack(self, source, target):
        # if source == target:
        #     return [source]

        path = []

        # _logger.debug('backtracking %s %s', source, target)
        current = target
        while current != source:
            path.append(current)
            # _logger.debug('append current %s', current)
            current = self.parent[current]
        path.append(current)

        #print('witness path', list(reversed(path)))
        #return self.dist[target]
        return list(reversed(path))


class DistPreprocessLarge:
    CACHE_FILENAME = 'untracked/astar/ch.pkl.cache'
    MAX_WITNESS_HOPS = 30

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
        self.rank = [0] * n
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
            with open(DistPreprocessLarge.CACHE_FILENAME, 'rb') as cache_:
                costs = pickle.load(cache_)
                # for line in cache_:
                #     landmark = [int(x) for x in line.strip().split()]
                #     costs.append(landmark)
            # _logger.info('Loaded CH edges from %s', DistPreprocessLarge.CACHE_FILENAME)
            return costs
        except IOError:
            return None

    def save_cache(self, obj):
        with open(DistPreprocessLarge.CACHE_FILENAME, 'wb') as cache_:
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
        queue = [] # PriorityQueue()
        for u in range(self.n):
            _new_shortcuts, u_importance = self.shortcut(u)
            # _logger.info('initial importance of %s = %s', u, u_importance)
            heappush(queue, (u_importance, u))

        neighbors = []
        is_neighbor = [False]*self.n

        outgoing_side = self.adj[0]
        incoming_side = self.adj[1]
        local_level = self.level

        while queue:
            _, u = heappop(queue)

            new_shortcuts, u_importance = self.shortcut(u)
            if not queue:
                # _logger.info('contract last %s', u)
                self.apply_shortcuts(new_shortcuts)
                self.complete_contraction(u)
                # for (u, w), (v, u_w_cost) in new_shortcuts.items():
                #     if self.add_arc(u, w, u_w_cost):
                #         self.shortcuts[(u, w)] = (v, u_w_cost)
                # self.mark_visited(u)
                # self.rank[u] = self.counter
                # self.counter += 1
                break

            #_logger.info('peeking %s', queue.queue[0])
            v_importance, _peeked_v = queue[0]
            #_v_new_shortcuts, peeked_v_importance = self.shortcut(peeked_v)
            # _logger.info('current importance of u %s = %s, v %s = %s',
            #              u, u_importance, peeked_v, v_importance)

            if u_importance > v_importance:
                # _logger.info('putting back to queue %s', u)
                #_logger.info('before %s', queue.queue[0])
                heappush(queue, (u_importance, u))
                #_logger.info('after %s', queue.queue[0])
                continue

            # _logger.info('contract %s', u)

            for x in outgoing_side[u]:
                if not is_neighbor[x]:
                    neighbors.append(x)
                    is_neighbor[x] = True
            for x in incoming_side[u]:
                if not is_neighbor[x]:
                    neighbors.append(x)
                    is_neighbor[x] = True

            self.apply_shortcuts(new_shortcuts)
            self.complete_contraction(u)
            # for (u, w), (v, u_w_cost) in new_shortcuts.items():
            #     if self.add_arc(u, w, u_w_cost):
            #         self.shortcuts[(u, w)] = (v, u_w_cost)
            # self.mark_visited(u)
            # self.rank[u] = self.counter
            # self.counter += 1

            for x in neighbors:
                is_neighbor[x] = False
                if x != u:
                    local_level[x] = max(local_level[x], local_level[u] + 1)
            neighbors = []

        _logger.warning('# shortcuts: %s', len(self.shortcuts))

    def find_shortcuts(self, node):
        outgoing_nodes = self.adj[0][node]
        incoming_nodes = self.adj[1][node]
        local_forward_adj = self.adj[0]

        # 3. Try to find witness path
        #    Witness search: run one directional Dijkstra from each predecessor
        #    (no target, limit max cost, limit number of hops)

        # This bound may be too relaxed.
        #max_witness_path_cost = self.get_max_witness_path_cost(node)
        new_shortcuts = dict()
        # number of successors of v, that we need to shortcut to
        shortcut_cover = 0
        # this may look similar to shortcut_cover, but it's not. this is a
        # number of ACTUALLY added shortcuts. Remember, some of them may already
        # be present, so we only update cost. Such updates are not counted.
        # It's expected that num_added_shortcuts <= shortcut_cover
        num_added_shortcuts = 0
        searcher = self.witness_searcher

        #for (u_index, u), (w_index, w) in self.iter_candidates(node):
        for (u_index, u) in enumerate(incoming_nodes):

            # This is maximum for one pair of (u, v), (v, w). It's a very strict
            # bound.
            # max_witness_path_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]

            # Current incoming + max of all outgoing edges.
            max_outgoing = max(self.cost[0][node]) if self.cost[0][node] else 0
            max_witness_path_cost = self.cost[1][node][u_index] + max_outgoing

            # _logger.debug('  doing witness search from %s to all max=%s',
            #               u, max_witness_path_cost)
            searcher.query(u, -1, node, max_witness_path_cost,
                           DistPreprocessLarge.MAX_WITNESS_HOPS)
            # witness_path_cost = self.witness_searcher.query(u, w, node, max_witness_path_cost)

            for (w_index, w) in enumerate(outgoing_nodes):
                #max_witness_path_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
                # self.witness_searcher.query(u, w, node, max_witness_path_cost)

                #dist = self.witness_searcher.get_dist(w)
                dist = -1 if searcher.dist[w] == searcher.inf else searcher.dist[w]

                # _logger.debug('    witness path from u %s to w %s, cost %s', u, w, dist)
                if dist == -1:
                    u_w_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
                    new_shortcuts[(u, w)] = (node, u_w_cost)
                    shortcut_cover += 1

                    try:
                        local_forward_adj[u].index(w)
                    except ValueError:
                        # If here, new shortcut would have been added
                        num_added_shortcuts += 1
                    # for x in local_forward_adj[u]:
                    #     if x == w:
                    #         break
                    # else:
                    #     # If here, new shortcut would have been added
                    #     num_added_shortcuts += 1

        return new_shortcuts, num_added_shortcuts, shortcut_cover

    def apply_shortcuts(self, new_shortcuts):
        for (u, w), (v, u_w_cost) in new_shortcuts.items():
            if self.add_arc(u, w, u_w_cost):
                self.shortcuts[(u, w)] = (v, u_w_cost)

    def complete_contraction(self, node):
        self.mark_visited(node)
        self.rank[node] = self.counter
        self.counter += 1

    def iter_candidates(self, v):
        outgoing_nodes = self.adj[0][v]
        incoming_nodes = self.adj[1][v]
        for (u_index, u), (w_index, w) in product(enumerate(incoming_nodes),
                                                  enumerate(outgoing_nodes)):
            # TODO u != w???
            if u != w and not self.visited[0][u] and not self.visited[0][w]:
                yield (u_index, u), (w_index, w)

    # def get_max_witness_path_cost(self, node):
    #     # outgoing_nodes = self.adj[0][node]
    #     # incoming_nodes = self.adj[1][node]
    #
    #     # 1. Find max sum of all segments (incoming + outgoing edges)
    #     # for (u_index, u), (w_index, w) in product(enumerate(incoming_nodes),
    #     #                                           enumerate(outgoing_nodes)):
    #     max_u_w_cost = 0
    #     for (u_index, _u), (w_index, w) in self.iter_candidates(node):
    #         u_w_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
    #         max_u_w_cost = max(max_u_w_cost, u_w_cost)
    #
    #     # for (u_index, u), (w_index, w) in product(enumerate(incoming_nodes),
    #     #                                           enumerate(outgoing_nodes)):
    #     #     u_w_cost = self.cost[1][node][u_index] + self.cost[0][node][w_index]
    #     # 2. Find min w' -> w cost
    #     min_w_prime_w_cost = self.inf
    #     for w in self.adj[0][node]:
    #         for w_prime_index, w_prime in enumerate(self.adj[1][w]):
    #             if not self.visited[0][w] and not self.visited[0][w_prime]:
    #                 # TODO: min or max???
    #                 min_w_prime_w_cost = min(min_w_prime_w_cost,
    #                                          self.cost[1][w][w_prime_index])
    #
    #     #max_witness_path_cost = max_u_w_cost - min_w_prime_w_cost
    #     max_witness_path_cost = max_u_w_cost
    #     return max_witness_path_cost

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
        return not (a or b)

    # Makes shortcuts for contracting node v
    def shortcut(self, v):
        # Implement this method yourself
        outgoing_nodes = self.adj[0][v]
        incoming_nodes = self.adj[1][v]

        # Compute the node importance in the end
        #shortcut_count, shortcut_cover = self.contract(v, dry_run=True)
        new_shortcuts, num_added_shortcuts, shortcut_cover = self.find_shortcuts(v)
        edge_difference = num_added_shortcuts - len(outgoing_nodes) - len(incoming_nodes)

        contracted_neighbors = 0
        for u in outgoing_nodes:
            if self.visited[0][u]:
                contracted_neighbors += 1
        for u in incoming_nodes:
            if self.visited[0][u]:
                contracted_neighbors += 1

        # shortcut_cover = 0
        level = self.level[v]
        # Compute correctly the values for the above heuristics before computing the node importance
        importance = edge_difference + contracted_neighbors + shortcut_cover + level
        return new_shortcuts, importance

    # --- QUERY PART ----------------------------------------------------------

    def clear(self):
        for v in self.workset:
            self.dist[0][v] = self.dist[1][v] = self.inf
            self.visited[0][v] = self.visited[1][v] = False
        self.workset = []
        #del self.workset[:]
        #self.visited = [False] * self.n

    def query(self, source, target):
        # _logger.info('query %s -> %s', source, target)
        if source == target:
            return 0

        self.clear()
        queue = [[], []] #[PriorityQueue(), PriorityQueue()]

        self.dist[0][source] = self.dist[1][target] = 0
        heappush(queue[0], (0, source))
        heappush(queue[1], (0, target))

        self.estimate = self.inf
        while queue[0] or queue[1]:
            self.do_iteration(queue, 0)
            self.do_iteration(queue, 1)

        result = -1 if self.estimate == self.inf else self.estimate

        # _logger.setLevel(logging.DEBUG)
        # _logger.info('query %s -> %s result %s', source, target, result)
        if result != -1:
            self.backtrack(source, target)

        return result

    def do_iteration(self, queue, side):
        if not queue[side]:
            return None
        _, u = heappop(queue[side])

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
        # _logger.debug('visit %s, side %s', u, side)
        local_adj = self.adj
        local_dist = self.dist
        local_cost = self.cost
        local_workset = self.workset
        local_rank = self.rank
        local_parent = self.parent

        neighbors = local_adj[side][u]

        for v_index, v in enumerate(neighbors):
            #print(v, file=sys.stderr)

            # Consider only edges going up
            if local_rank[u] >= local_rank[v]:
                # _logger.debug('skipping due to rank(%s) %s >= rank(%s) %s',
                              # u, local_rank[u], v, local_rank[v])
                continue

            alt = local_dist[side][u] + local_cost[side][u][v_index]
            # _logger.debug('alt u v %s %s = %s', u, v, alt)

            if alt < local_dist[side][v]:
                # _logger.debug('new alt %s for u v %s %s side %s', alt, u, v, side)
                local_dist[side][v] = alt
                local_parent[side][v] = u
                heappush(queue[side], (alt, v))
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
        # _logger.debug('path first part HUMAN %s', self._human_path(path))

        last = u_best
        while last != target:
            last = self.parent[1][last]
            path.append(last)
        # _logger.debug('path first+last part HUMAN %s', self._human_path(path))

        path = self.expand_shortcuts(path)
        #print(' '.join(map(lambda x: str(x+1), path)))
        # _logger.debug('result path HUMAN %s', self._human_path(path))
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
                # _logger.debug('expanded %s %s %s = %s', u, v, w, _cost)
                queue.appendleft(w)
                queue.appendleft(v)
                queue.appendleft(u)
                # _logger.debug('queue %s', queue)
            else:
                # _logger.debug('not a shortcut %s %s', u, w)
                result.append(u)
                queue.appendleft(w)
                # _logger.debug('queue %s result %s', queue, result)
        result.append(queue.popleft())

        # _logger.debug('path after expansion %s', self._human_path(result))
        return result


# def readl():
#     return map(int, sys.stdin.readline().split())


def readl(file_=None):
    if file_ is None:
        file_ = sys.stdin
    return map(int, file_.readline().strip().split())


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    file_ = open(filename) if filename else None

    n, m = readl(file_)
    adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
    cost = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for _ in range(m):
        u, v, c = readl(file_)
        adj[0][u-1].append(v-1)
        cost[0][u-1].append(c)
        adj[1][v-1].append(u-1)
        cost[1][v-1].append(c)

    ch = DistPreprocessLarge(n, m, adj, cost)
    print("Ready")
    sys.stdout.flush()
    #ch.save_to_file('untracked/contracted.large.in')

    t, = readl(file_)
    for _ in range(t):
        s, t = readl(file_)
        print(ch.query(s-1, t-1))

    if file_:
        file_.close()


if __name__ == '__main__':
    main()
