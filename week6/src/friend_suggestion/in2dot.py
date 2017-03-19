#import fileinput
import sys
import itertools

def get_path(filename):
    with open(filename) as file_:
        path = [int(v) for v in file_.readline().strip().split()]
    return path

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def main():
    filename = sys.argv[1]
    path_filename = sys.argv[2]
    print('digraph %s {' % filename.replace('.', '_').replace('-', '_'))
    print('''
splines=true;
sep="+25,25";
overlap=scalexy;
nodesep=0.6;
node [fontsize=12 arrowsize=0.1];
edge [fontsize=8 arrowsize=0.6 len=2];
''')
    path = set(pairwise(get_path(path_filename)))

    with open(filename) as file_:
        num_vertices, num_edges = file_.readline().strip().split()
        num_vertices, num_edges = int(num_vertices), int(num_edges)

        # Read edges into a buffer
        edges = []
        for _ in range(num_edges):
            u, v, c = file_.readline().strip().split()
            edges.append((int(u), int(v), c))

        # Skip queries
        num_queries, = file_.readline().strip().split()
        s, t = None, None
        for _ in range(int(num_queries)):
            if s is None:
                s, t = file_.readline().strip().split()
            else:
                file_.readline()

        # Read shortcuts
        shortcuts = dict()
        num_shortcuts, = file_.readline().strip().split()
        for _ in range(int(num_shortcuts)):
            u, v = file_.readline().strip().split()
            shortcuts[(int(u), int(v))] = None

        # Draw edges
        for u, v, c in edges:
            color = "#FF0000A0" if (int(u), int(v)) in path else "#00000050"
            style = 'style=dashed' if (u, v) in shortcuts else ''
            print('    %s -> %s [label="%s" color="%s" %s];' % (u, v, c, color, style))

        try:
            #file_.readline()
            #s, t = file_.readline().strip().split()
            print('labelloc="t";')
            title = '%s => %s (%s nodes, %s edges)' % (s, t, num_vertices, num_edges)
            print('label="%s";' % title)
        except ValueError:
            # This graph probably does not contain queries
            pass

    print('}')


if __name__ == '__main__':
    main()
