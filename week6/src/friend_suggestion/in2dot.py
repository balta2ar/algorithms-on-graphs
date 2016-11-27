#import fileinput
import sys
import itertools

def get_path(filename):
    with open(filename) as file:
        path = [int(v) for v in file.readline().strip().split()]
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
    print('edge [len=2];')
    path = set(pairwise(get_path(path_filename)))

    with open(filename) as file:
        nv, ne = file.readline().strip().split()
        nv, ne = int(nv), int(ne)

        for i in range(ne):
            u, v, c = file.readline().strip().split()
            color = "red" if (int(u), int(v)) in path else "black"
            print('    %s -> %s [label="%s" color="%s"];' % (u, v, c, color))

    print('}')


if __name__ == '__main__':
    main()
