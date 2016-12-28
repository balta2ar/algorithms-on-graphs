import sys


def generate_square(n, straight_cost=1, diagonal_cost=2):
    coords = []
    edges = [[] for _ in range(n*n)]

    # columns
    for column in range(n):
        # rows
        for row in range(n):
            coords.append((column+1, row+1))
            u = column * n + row
            #print(column, row, u)
            # horizontal
            if column < n-1:
                edges[u].append((u+n, straight_cost))
            # vertical
            if row < n-1:
                edges[u].append((u+1, straight_cost))
            # diagonal up
            if column < n-1 and row > 0:
                edges[u].append((u+n-1, diagonal_cost))
            # diagonal down
            if row < n-1 and column < n-1:
                edges[u].append((u+n+1, diagonal_cost))

    return n*n, sum([len(es) for es in edges]), coords, edges


def to_string(n, m, coords, edges):
    #return str((coords, edges))
    #return ''
    output = []
    output.append('%d %d' % (n, m))
    for x, y in coords:
        output.append('%d %d' % (x, y))
    for u, neighbors in enumerate(edges):
        for v, cost in neighbors:
            output.append('%d %d %d' % (u+1, v+1, cost))
    output.append('1')
    output.append('1 %d' % (n))

    return '\n'.join(output)


def main():
    n = int(sys.argv[1])
    n, m, coords, edges = generate_square(n)
    print(to_string(n, m, coords, edges))


if __name__ == '__main__':
    main()
