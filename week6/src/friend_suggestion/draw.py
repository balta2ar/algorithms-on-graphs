import sys
import pickle
#from math import sqrt
import numpy as np
import random
from graph_tool.all import *


def get_layout(g, filename):
    try:
        pos = random_layout(g)
        with open(filename, 'rb') as file:
            a = pickle.load(file)
            pos.set_2d_array(a)
            return pos
    except Exception:
        pos = sfdp_layout(g)
        #from ipdb import set_trace; set_trace()
        a = pos.get_2d_array(range(g.num_vertices()))
        with open(filename, 'wb') as file:
            pickle.dump(a, file, -1)
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


def main():
    source = sys.argv[1]
    colored = sys.argv[2]
    dest = sys.argv[3]
    print('Reading %s' % source)
    g = load_graph(source)
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
    pos = get_layout(g, 'layout/%s.pos' % source)
    #pos = random_layout(g)
    #pos = sfdp_layout(g, pos=pos)
    # from ipdb import set_trace; set_trace()
    color = get_colored(g, colored)

    graph_draw(g, pos,
               vertex_text=g.vertex_index,
               vertex_size=1,
               vertex_font_size=2,
               vertex_color=[0,1,1,0],
               #vertex_fill_color=[0.6,1,0,0.9],
               vertex_fill_color=color,
               #vertex_color=color,
               edge_pen_width=0.2,
               edge_marker_size=1,
               output=dest)


if __name__ == '__main__':
    main()
