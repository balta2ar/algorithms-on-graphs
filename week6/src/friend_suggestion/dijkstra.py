# Zaz Brown
# github.com/zaz/dijkstra
"""An efficient algorithm to find shortest paths between nodes in a graph."""
import sys
from collections import defaultdict
from copy import deepcopy


def create_reference_dijkstra(n, m, adj, cost):
    d = Digraph()
    for u in range(n):
        for v_index, v in enumerate(adj[0][u]):
            c = cost[0][u][v_index]
            d.addEdge(u, v, c)
    return d


class ReferenceDijkstra:
    def __init__(self, n, m, adj, cost):
        self.d = create_reference_dijkstra(n, m, adj, cost)

    def query(self, source, target):
        return self.d.query(source, target)


class Digraph(object):
    def __init__(self, nodes=[]):
        self.nodes = set()
        self.neighbours = defaultdict(set)
        self.dist = {}

    def addNode(self, *nodes):
        [self.nodes.add(n) for n in nodes]

    def addEdge(self, frm, to, d=1e309):
        self.addNode(frm, to)
        self.neighbours[frm].add(to)
        self.dist[frm, to] = d

    def dijkstra(self, start, maxD=1e309):
        """Returns a map of nodes to distance from start and a map of nodes to
        the neighbouring node that is closest to start."""
        # total distance from origin
        tdist = defaultdict(lambda: 1e309)
        tdist[start] = 0
        # neighbour that is nearest to the origin
        preceding_node = {}
        unvisited = deepcopy(self.nodes)
        #unvisited = self.nodes

        while unvisited:
            current = unvisited.intersection(tdist.keys())
            if not current: break
            min_node = min(current, key=tdist.get)
            unvisited.remove(min_node)

            for neighbour in self.neighbours[min_node]:
                d = tdist[min_node] + self.dist[min_node, neighbour]
                if tdist[neighbour] > d and maxD >= d:
                    tdist[neighbour] = d
                    preceding_node[neighbour] = min_node

        return tdist, preceding_node

    def min_path(self, start, end, maxD=1e309):
        """Returns the minimum distance and path from start to end."""
        tdist, preceding_node = self.dijkstra(start, maxD)
        dist = tdist[end]
        backpath = [end]
        try:
            while end != start:
                end = preceding_node[end]
                backpath.append(end)
            path = list(reversed(backpath))
        except KeyError:
            path = None

        dist = -1 if dist == 1e309 else dist
        return dist, path

    def query(self, *args): return self.min_path(*args)[0]
    def dist_to(self, *args): return self.min_path(*args)[0]
    def path_to(self, *args): return self.min_path(*args)[1]


def main():
    filename = sys.argv[1]
    with open(filename) as file:
        n, m = file.readline().strip().split()
        n, m = int(n), int(m)

        d = Digraph()
        for i in range(m):
            u, v, c = file.readline().strip().split()
            u, v, c = int(u), int(v), int(c)
            d.addEdge(u-1, v-1, c)

        nr = int(file.readline().strip())
        for i in range(nr):
            frm, to = file.readline().strip().split()
            frm, to = int(frm), int(to)
            #print(frm, to, d.min_path(frm, to))
            print(d.dist_to(frm-1, to-1))


if __name__ == '__main__':
    main()

