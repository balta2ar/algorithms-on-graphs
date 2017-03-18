import os
import sys
import time
import random
from copy import deepcopy

from dist_preprocess_small import DistPreprocessSmall
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
            self._eliminate_edges()
            self._remove_isolated_nodes()

            self._verify()
            # time.sleep(0.5)

    def _verify(self):
        if self._is_mismatch():
            self._save()
        else:
            self._restore()

    def _is_mismatch(self):
        dijk = DijkstraOnedirectional(self.n, self.m, self.adj,
                                      deepcopy(self.cost), None, None)
        a = dijk.query(self.s-1, self.t-1)
        print('a = %s' % a)
        ch = DistPreprocessSmall(self.n, self.m, deepcopy(self.adj),
                                 deepcopy(self.cost), None, None)
        b = ch.query(self.s-1, self.t-1)
        print('b = %s' % b)
        result = a < b
        print('is_mismatch %s' % result)
        return result

    def _save(self):
        temp_filename = self.output_filename + '.tmp'
        with open(temp_filename, 'w') as file_:
            file_.write('%s %s\n' % (self.n, self.m))
            for u, vs in enumerate(self.adj[0]):
                for v_index, v in enumerate(vs):
                    file_.write('%s %s %s\n' % (u+1, v+1, self.cost[0][u][v_index]))
            file_.write('1\n')
            file_.write('%s %s\n' % (self.s, self.t))
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

    def _eliminate_edges(self):
        ok, u, v = self._pick_edge()
        #ok, u, v, v_index = True, 39, 91, 17
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
            if len(self.adj[0][i]) == 0 and len(self.adj[1][i]) == 0:
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
