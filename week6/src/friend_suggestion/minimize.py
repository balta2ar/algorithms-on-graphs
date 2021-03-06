import os
import sys
import time
import random
from math import ceil
from copy import deepcopy

from dist_preprocess_small import DistPreprocessSmall
from dist_preprocess_large import DistPreprocessLarge
from friend_suggestion import DijkstraOnedirectional


def readl(file_=None):
    if file_ is None:
        file_ = sys.stdin
    return map(int, file_.readline().strip().split())


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


def read_graph_from_file(filename):
    print('Reading from file %s' % filename)
    with open(filename) as file_:
        n, m = readl(file_)

        # x = [0 for _ in range(n)]
        # y = [0 for _ in range(n)]
        # for i in range(n):
        #     a, b = readl(file_)
        #     x[i] = a
        #     y[i] = b

        # adj = [[] for _ in range(n)]
        # cost = [[] for _ in range(n)]
        # for _ in range(m):
        #     u, v, c = readl()
        #     adj[u-1].append(v-1)
        #     cost[u-1].append(c)

        adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
        cost = [[[] for _ in range(n)], [[] for _ in range(n)]]
        for _ in range(m):
            u, v, c = readl(file_)
            adj[0][u-1].append(v-1)
            cost[0][u-1].append(c)
            adj[1][v-1].append(u-1)
            cost[1][v-1].append(c)

        t, = readl(file_)
        s, t = readl(file_)

    print('From file', n, m, s, t)
    return n, m, adj, cost, None, None, s, t


class GraphMinimizer(object):
    def __init__(self, n, m, adj, cost, s, t, output_filename):
        self.n = n
        self.m = m
        self.adj = adj
        self.cost = cost
        self.s = s
        self.t = t
        self.output_filename = output_filename
        self.backup = n, m, deepcopy(adj), deepcopy(cost), s, t

    def __call__(self):
        #random.seed(1)
        # +1. Remove isolated nodes
        # 2. Try to collapse start->end path, find shorter solutions
        # 3. Try other random source/target nodes
        while self.n > 0:
            #n, m, adj, cost, _x, _y, s, t = read_graph_from_file('minimize.in')
            print('n, m, s, t', self.n, self.m, self.s, self.t)
            self._eliminate_edges(random.randint(1, 5))
            self._remove_isolated_nodes()

            # if self._get_min_cost() > 1:
            #     self._verify()
            #     self._minimize_cost()
            #     self._verify()

            mismatch, a_dist, a_path, _b_dist, _b_path = self._verify()
            print('verify results', mismatch, a_dist, a_path, 's t', self.s, self.t)

            if not mismatch and a_dist > 0 and len(a_path) > 2:
                self._shorten_path(a_path)
                self._verify()

            #time.sleep(0.5)

    def _verify(self):
        mismatch, a_dist, a_path, b_dist, b_path = self._is_mismatch()
        if mismatch:
            self._save()
        else:
            self._restore()
        return mismatch, a_dist, a_path, b_dist, b_path

    def _is_mismatch(self):
        if self.s == self.t:
            return False, -1, [], -1, []

        print('is_mismatch s t', self.s, self.t)
        dijk = DijkstraOnedirectional(self.n, self.m, self.adj,
                                      deepcopy(self.cost), None, None)
        a_dist = dijk.query(self.s-1, self.t-1)
        #print('a_dist after query %s' % a_dist)
        _, a_path = dijk.backtrack(self.s-1, self.t-1) if a_dist != -1 else (None, [])
        print('is_mismatch a_dist = %s, a_path = %s' % (a_dist, a_path))
        ch = DistPreprocessLarge(self.n, self.m, deepcopy(self.adj),
                                 deepcopy(self.cost), None, None)
        b_dist = ch.query(self.s-1, self.t-1)
        print('is_mismatch b_dist = %s' % b_dist)
        _, b_path = ch.backtrack(self.s-1, self.t-1) if b_dist != -1 else (None, [])
        print('is_mismatch b_dist = %s, b_path = %s' % (b_dist, b_path))
        result = a_dist < b_dist
        #print('is_mismatch %s' % result)
        return result, a_dist, a_path, b_dist, b_path

    def _save(self):
        temp_filename = self.output_filename + '.tmp'
        with open(temp_filename, 'w') as file_:
            file_.write('%s %s\n' % (self.n, self.m))
            for u, vs in enumerate(self.adj[0]):
                for v_index, v in enumerate(vs):
                    file_.write('%s %s %s\n' % (u+1, v+1, self.cost[0][u][v_index]))
            file_.write('1\n') # requests
            file_.write('%s %s\n' % (self.s, self.t))
            file_.write('0\n') # shortcuts
        os.rename(temp_filename, self.output_filename)
        self.backup = (self.n, self.m,
                       deepcopy(self.adj), deepcopy(self.cost),
                       self.s, self.t)
        print('Saved to minimize.in')

    def _restore(self):
        print('Restoring')
        n, m, adj, cost, s, t = self.backup
        self.n = n
        self.m = m
        self.adj = deepcopy(adj)
        self.cost = deepcopy(cost)
        self.s = s
        self.t = t

    def _minimize_cost(self):

        # print('min_cost', min_cost)
        # self._reduce_cost(self.cost[0], min_cost-1)
        # self._reduce_cost(self.cost[1], min_cost-1)
        self._divide_cost(self.cost[0], 2)
        self._divide_cost(self.cost[1], 2)

    def _get_min_cost(self):
        min_cost = None
        for us in self.cost[0]:
            for u in us:
                min_cost = u if min_cost is None else min(min_cost, u)
        return min_cost if min_cost is not None else -1

    def _reduce_cost(self, costs, delta):
        for node_costs in costs:
            for i, _ in enumerate(node_costs):
                node_costs[i] -= delta

    def _divide_cost(self, costs, divider):
        for node_costs in costs:
            for i, _ in enumerate(node_costs):
                #node_costs[i] = round(node_costs[i] / divider)
                node_costs[i] = ceil(node_costs[i] / divider)

    def _shorten_path(self, reference_path):
        candidates = reference_path[1:-1]
        old_s = self.s
        self.s = random.choice(candidates) + 1
        print('shortest_path reference_path: %s' % reference_path)
        print('Trying new s %s instead of old s %s' % (self.s, old_s))

    def _eliminate_edges(self, num_edges):
        for _ in range(num_edges):
            ok, u, v = self._pick_edge()
            if ok:
                print('picked', u, v)
                self._remove_edge(u, v)
                self.m -= 1
            else:
                print('could not pick edge')

    def _pick_edge(self):
        u = random.randint(0, self.n-1)
        vs = self.adj[0][u]
        if vs:
            v_index = random.randint(0, len(vs)-1)
            v = self.adj[0][u][v_index]
            return True, u, v # , v_index
        return False, None, None

    def _remove_edge(self, u, v):
        print('removing %s %s' % (u, v))
        index_1 = self.adj[0][u].index(v)
        index_2 = self.adj[1][v].index(u)
        del self.adj[0][u][index_1]
        del self.cost[0][u][index_1]
        del self.adj[1][v][index_2]
        del self.cost[1][v][index_2]

    def _remove_isolated_nodes(self):
        last_isolated_node = None
        for i in range(len(self.adj[0])-1, -1, -1):
        #for i in range(0, len(adj[0])):
            if not self.adj[0][i] and not self.adj[1][i]:
                last_isolated_node = i
                break

        print('isolated %s '% last_isolated_node)
        if last_isolated_node is None:
            return
            #return False, n, s, t

        self._remove_isolated_node(last_isolated_node)
        self.n -= 1
        self.s = self.s-1 if last_isolated_node < self.s-1 else self.s
        self.t = self.t-1 if last_isolated_node < self.t-1 else self.t
        #return True, n, s, t

    def _remove_isolated_node(self, u):
        self._update_nodes_references(self.adj[0], u)
        self._update_nodes_references(self.adj[1], u)
        del self.adj[0][u]
        del self.adj[1][u]
        del self.cost[0][u]
        del self.cost[1][u]

    def _update_nodes_references(self, nodes, u):
        """
        nodes = [[], [1,2,3], [], [4]]
        u - node to remove.
        update all nodes id that are greater than u.
        """
        for us in nodes:
            for i, _ in enumerate(us):
                if us[i] > u:
                    us[i] -= 1


def main():
    #n, m, adj, cost = read_from_stdin()
    #n, m, adj, cost, _x, _y = read_graph_from_file('test1/case3-1-min.in')
    filename = 'minimize.in'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    n, m, adj, cost, _x, _y, s, t = read_graph_from_file(filename)
    #t, = readl()
    #s, t = readl()
    #s, t = 54, 73
    #minimize_graph(n, m, adj, cost, s, t)
    minimizer = GraphMinimizer(n, m, adj, cost, s, t, filename)
    minimizer()


if __name__ == '__main__':
    main()
