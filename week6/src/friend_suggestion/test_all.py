import unittest

from dijkstra import ReferenceDijkstra
from friend_suggestion import DijkstraOnedirectional
from friend_suggestion import DijkstraBidirectional
from dist_with_coords import AStarOnedirectional
from dist_with_coords import AStarBidirectional
from landmarks import BreadthFirstSearchOneToAll
from landmarks import LandmarksAStarOnedirectional
from landmarks import LandmarksAStarBidirectional
from dist_preprocess_small import DistPreprocessSmall
from dist_preprocess_large import DistPreprocessLarge


def readl(file_):
    return list(map(int, file_.readline().strip().split()))


def read_graph_from_file(filename, with_coords=True):
    with open(filename) as file_:
        n, m = readl(file_)

        x, y = None, None
        if with_coords:
            try:
                x = [0 for _ in range(n)]
                y = [0 for _ in range(n)]
                for i in range(n):
                    a, b = readl(file_)
                    x[i] = a
                    y[i] = b
            except ValueError:
                # ok, this graph probably does not have coords, let's try
                # without them
                return read_graph_from_file(filename, with_coords=False)

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

    return n, m, adj, cost, x, y


def read_queries_from_file(filename, with_coords=True):
    with open(filename) as file_:
        n, m = readl(file_)
        skip_count = n + m if with_coords else m
        for _ in range(skip_count):
            readl(file_)
        try:
            n = readl(file_)[0]
        except IndexError:
            return read_queries_from_file(filename, with_coords=False)
        return [readl(file_) for _ in range(n)]


def read_lines_from_file(filename):
    with open(filename) as file_:
        return [int(line.strip()) for line in file_.readlines()]


class TestDistPreprocessLarge(unittest.TestCase):
    def _compare(self, input_filename, output_filename):
        n, m, adj, cost, x, y = read_graph_from_file(input_filename)
        alg = DistPreprocessLarge(n, m, adj, cost, x, y)
        #alg = DijkstraOnedirectional(n, m, adj, cost, x, y)
        #alg = AStarBidirectional(n, m, adj, cost, x, y)
        #alg = AStarOnedirectional(n, m, adj, cost, x, y)
        queries = read_queries_from_file(input_filename)
        actual = [alg.query(s-1, t-1) for s, t in queries]
        expected = read_lines_from_file(output_filename)
        self.assertEqual(expected, actual)

        self._check_all_queries(input_filename, output_filename)

    def _check_all_queries(self, input_filename, output_filename):
        n, m, adj, cost, x, y = read_graph_from_file(input_filename)
        dijk = DijkstraOnedirectional(n, m, adj, cost, x, y)
        ch = DistPreprocessSmall(n, m, adj, cost, x, y)
        #alg = AStarBidirectional(n, m, adj, cost, x, y)
        #alg = AStarOnedirectional(n, m, adj, cost, x, y)
        #queries = read_queries_from_file(input_filename)

        for u in range(n):
            for v in range(n):
                a = dijk.query(u, v)
                b = ch.query(u, v)
                self.assertEqual(a, b)
                # answers = set([ch.query(u-1, v-1),
                #                dijk.query(u-1, v-1)])
                # self.assertEqual(1, len(answers))
        # actual1 = [alg.query(s-1, t-1) for s, t in queries]
        # expected = read_lines_from_file(output_filename)
        # self.assertEqual(expected, actual)

    def test_sample1(self):
        self._compare('test_astar/sample1.in', 'test_astar/sample1.out')

    def test_sample2(self):
        self._compare('test_astar/sample2.in', 'test_astar/sample2.out')

    def test_case1(self):
        self._compare('test_astar/case1.in', 'test_astar/case1.out')

    def test_case2(self):
        self._compare('test_astar/case2.in', 'test_astar/case2.out')

    def test_case2_1_min(self):
        self._compare('test_ch/case2-1-min.in', 'test_ch/case2-1-min.out')

    def test_case3_1_min(self):
        self._compare('test_ch/case3-1-min.in', 'test_ch/case3-1-min.out')

    # def test_case3(self):
    #     self._compare('test_astar/case3.in', 'test_astar/case3.out')

    # def test_gen10(self):
    #     self._compare('test_astar/gen10.in', 'test_astar/gen10.out')

    # def test_gen100(self):
    #     self._compare('test_astar/gen100.in', 'test_astar/gen100.out')

    # def test_gen1000(self):
    #     self._compare('test_astar/gen1000.in', 'test_astar/gen1000.out')
