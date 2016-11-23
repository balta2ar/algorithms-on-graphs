#import fileinput
import sys


def main():
    filename = sys.argv[1]
    print('digraph %s {' % filename.replace('.', '_').replace('-', '_'))
    print('edge [len=2];')

    with open(filename) as file:
        nv, ne = file.readline().strip().split()
        nv, ne = int(nv), int(ne)

        for i in range(ne):
            u, v, c = file.readline().strip().split()
            print('    %s -> %s [label="%s"];' % (u, v, c))

    print('}')


if __name__ == '__main__':
    main()
