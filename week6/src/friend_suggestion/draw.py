import sys
import pickle
#from math import sqrt
import numpy as np
import random
from graph_tool.all import *


def get_layout(g, filename):
    pkl = '%s.pkl' % filename
    txt = '%s.txt' % filename

    try:
        pos = random_layout(g)
        with open(pkl, 'rb') as file:
            a = pickle.load(file)
            pos.set_2d_array(a)

            with open(txt, 'w') as file:
                for v in g.vertices():
                    p = pos[v]
                    #from ipdb import set_trace; set_trace()
                    file.write('%f %f\n' % (p[0], p[1]))
                #for i in range(g.num_vertices()):
                #    file.write('%f %f\n' % (a[0][i], a[1][i]))

            return pos
    except Exception:
        pos = sfdp_layout(g)
        a = pos.get_2d_array(range(g.num_vertices()))
        with open(pkl, 'wb') as file:
            pickle.dump(a, file, -1)

        with open(txt, 'w') as file:
            for v in g.vertices():
                p = pos[v]
                file.write('%f %f\n' % (p[0], p[1]))
        # with open(txt, 'w') as file:
        #     for i in range(g.num_vertices()):
        #         file.write('%f %f\n' % (a[0][i], a[1][i]))
        return pos


def get_colored(g, filename):
    with open(filename) as file:
        path = [int(v) for v in file.readline().strip().split()]

    color = g.new_vertex_property("vector<double>")
    for v in g.vertices():
        if int(v) in path:
            color[v] = [0.6, 1, 0, 0.9]
        else:
            color[v] = [0.6, 0, 0, 0.9]
    return color


def read_graph(filename):
    #edges = []
    g = Graph()
    with open(filename) as file:
        n, m = file.readline().strip().split()
        n, m = int(n), int(m)

        g.add_vertex(n)
        for i in range(m):
            u, v, c = file.readline().strip().split()
            u, v, c = int(u)-1, int(v)-1, int(c)
            g.add_edge(u, v)
            #edges.append((u, v))
    return g


def main():
    source = sys.argv[1]
    colored = sys.argv[2]
    dest = sys.argv[3]
    print('Reading %s' % source)
    #g = load_graph(source)
    g = read_graph(source)
    print('Drawing to %s' % dest)

    random.seed(0)
    np.random.seed(0)

    deg = g.degree_property_map("in")
    deg.a = 2 * (np.sqrt(deg.a) * 0.5 + 0.4)
    ebet = betweenness(g)[1]
    #graphviz_draw(g, vcolor=deg, vorder=deg, elen=10,
    #              ecolor=ebet, eorder=ebet, output=dest)
    #graph_draw(g, vcolor=deg, vorder=deg, elen=10,
    #           ecolor=ebet, eorder=ebet, output=dest)
    #graph_draw(g, output=dest)
    #age = g.vertex_properties['age']
    pos = get_layout(g, '%s.pos' % source)
    #pos = random_layout(g)
    #pos = sfdp_layout(g, pos=pos)
    color = get_colored(g, colored)

    graph_draw(g, pos,
               vertex_text=g.vertex_index,
               vertex_size=10,
               vertex_font_size=20,
               vertex_color=[0,1,1,0],
               #vertex_fill_color=[0.6,1,0,0.9],
               vertex_fill_color=color,
               #vertex_color=color,
               edge_pen_width=10 * 0.2,
               edge_marker_size=10,
               output=dest)


if __name__ == '__main__':
    main()
