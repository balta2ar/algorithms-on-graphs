import sys



def draw_graph_pillow(visited, coordinates, output):
    from PIL import Image, ImageDraw

    image = Image.new('RGB', (20, 20), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for line in open(coordinates):
        x, y = line.split()
        x, y = float(x), float(y)
        draw.point((x, y), fill=(255, 0, 0))
        #print(x, y)
    image.save(output)


def read_graph(filename):
    edges = []
    with open(filename) as file:
        n, m = file.readline().strip().split()
        n, m = int(n), int(m)

        for i in range(m):
            u, v, c = file.readline().strip().split()
            u, v, c = int(u)-1, int(v)-1, int(c)
            edges.append((u, v))
    return edges


def read_coords(filename):
    coords = []
    for line in open(filename):
        x, y = line.split()
        x, y = float(x), float(y)
        coords.append((x, y))
    return coords

def read_visited(filename):
    nodes = []
    for line in open(filename):
        node = int(line.strip())
        nodes.append(node)
    return nodes


def draw_graph_cairo(input_graph, visited_filename, coordinates, output):
    import cairo
    from math import pi

    edges = read_graph(input_graph)
    coords = read_coords(coordinates)

    WIDTH, HEIGHT, SCALE = 2000, 2000, 40
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(-WIDTH, -HEIGHT, WIDTH*2, HEIGHT*2)
    ctx.fill()

    w = h = 0.3
    offset = 0.15
    ctx.translate(WIDTH/2. + 200, HEIGHT/2. - 200)
    ctx.scale(SCALE, SCALE)

    def draw_line(x1, y1, x2, y2):
        ctx.save()
        ctx.move_to(x1 + offset, y1 + offset)
        ctx.line_to(x2 + offset, y2 + offset)
        ctx.stroke()
        ctx.restore()

    def draw_circle(x, y, w, h):
        ctx.save()
        ctx.translate(x + w / 2., y + h / 2.)
        ctx.scale(w / 2., h / 2.)
        ctx.arc(0., 0., 1., 0., 2 * pi)
        ctx.stroke()
        ctx.restore()

    for (x, y) in coords:
        ctx.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        ctx.set_line_width(0.6)
        draw_circle(x, y, w, h)
        #print(x, y)

    for (u, v) in edges: #[:10]:
        a, b = coords[u], coords[v]
        ctx.set_source_rgba(0.5, 0.5, 0.5, 0.3)
        ctx.set_line_width(0.1)
        draw_line(a[0], a[1], b[0], b[1])

    i = 0
    #surface.write_to_png(output)
    surface.write_to_png('frames/%06d.png' % i)
    return

    visited = read_visited(visited_filename)
    for node in visited:
        x, y = coords[node]

        ctx.set_source_rgba(0.9, 0.1, 0.1, 0.7)
        ctx.set_line_width(0.5)
        draw_circle(x, y, w, h)
        surface.write_to_png('frames/%06d.png' % i)
        i += 1
        #if i > 10:
        #    break

def main():
    input_graph = sys.argv[1]
    visited = sys.argv[2]
    coordinates = sys.argv[3]
    output = sys.argv[4]
    #visited = sys.argv[2]

    print('Drawing to %s' % output)
    #draw_graph_pillow(visited, coordinates, output)
    draw_graph_cairo(input_graph, visited, coordinates, output)


if __name__ == '__main__':
    main()
