import sys
import argparse
from os.path import basename, dirname, isfile

import cairo
from math import pi
import numpy as np


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


def read_graph(filename, with_coords=False):
    edges = []
    with open(filename) as file:
        n, m = file.readline().strip().split()
        n, m = int(n), int(m)

        if with_coords:
            coords = np.empty((n, 2))
            for i in range(n):
                x, y = file.readline().strip().split()
                x, y = float(x), float(y)
                coords[i] = (x, y)

        for i in range(m):
            u, v, c = file.readline().strip().split()
            u, v, c = int(u)-1, int(v)-1, int(c)
            edges.append((u, v))

    return edges, coords if with_coords else edges


def read_coords(filename):
    with open(filename) as file:
        n = int(file.readline().strip())
        coords = np.empty((n, 2))
        for i in range(n):
            x, y = file.readline().strip().split()
            x, y = float(x), float(y)
            coords[i] = (x, y)
    return coords

def read_visited(filename):
    nodes = []
    for line in open(filename):
        node = int(line.strip())
        nodes.append(node)
    return nodes


def draw_graph_cairo(input_graph, visited_filename, coordinates, output, size):

    if coordinates:
        edges = read_graph(input_graph)
        coords = read_coords(coordinates)
    else:
        edges, coords = read_graph(input_graph, with_coords=True)

    WIDTH, HEIGHT = size, size

    smallest_side = min(WIDTH, HEIGHT)
    while (coords.max() - coords.min()) > smallest_side:
        coords = coords / 10.
        print('Scaled down by 10, max min = %s %s' % (coords.max(), coords.min()))

    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    dw, dh = max_x - min_x, max_y - min_y
    print('dw dh', dw, dh)
    print('mins', min_x, min_y, max_x, max_y)
    ratiow, ratiov = WIDTH / dw, HEIGHT / dh
    #ratiow, ratiov = ratiow * 0.95, ratiov * 0.95
    scale = min(ratiow, ratiov)
    print('ratios', ratiow, ratiov)

    #w = h = 0.3
    #offset = 0.15
    w = h = max(dw, dh) / 500.
    offset = w / 2.
    #text_offset = offset * 2
    print('circle w h %s offset %s' % (w, offset))
    vertice_w, edge_w, visited_w = 0.6, w, 0.5 * 10
    print('vertice_w %s edge_w %s visited_w %s' % (vertice_w, edge_w, visited_w))

    #ctx.translate(WIDTH/2. + 200, HEIGHT/2. - 200)
    #ctx.scale(SCALE, SCALE)
    #ctx.translate(min_x + dw/2., min_y + dh/2.)
    #tx, ty = dw * ratiow / 2. + min_x, dh * ratiov / 2. + min_y
    #tx, ty = WIDTH/2. + min_x - dw, HEIGHT/2. + min_y - dh
    tx, ty = -min_x, -min_y
    print('ts', tx, ty)
    num = None # 10000

    def draw_line(ctx, x1, y1, x2, y2):
        ctx.save()
        ctx.move_to(x1 + offset, y1 + offset)
        ctx.line_to(x2 + offset, y2 + offset)
        ctx.stroke()
        ctx.restore()

    def draw_circle(ctx, x, y, w, h):
        ctx.save()
        ctx.translate(x + w / 2., y + h / 2.)
        ctx.scale(w / 2., h / 2.)
        ctx.arc(0., 0., 1., 0., 2 * pi)
        ctx.stroke()
        ctx.restore()

    # def draw_text(ctx, x, y, text):
    #     ctx.save()
    #     ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    #     ctx.set_font_size(0.2)
    #     ctx.set_source_rgb(0, 0, 0)
    #     ctx.move_to(x, y)
    #     #ctx.show_text(text)
    #     ctx.restore()

    def draw_vertices(ctx):
        limited = coords[:num] if num is not None else coords
        print('Drawing %d vertices' % len(limited))
        for i, (x, y) in enumerate(limited):
            sys.stdout.write('%0.02f   \r' % (100. * i / len(limited)))
            sys.stdout.flush()
            ctx.set_source_rgba(0.5, 0.5, 0.5, 0.7)
            #draw_text(ctx, x + text_offset, y + 2 * text_offset, str(i))
            ctx.set_line_width(vertice_w)
            draw_circle(ctx, x, y, w, h)
            #print(x, y)
        print('')

    def draw_edges(ctx):
        limited = edges[:num] if num is not None else edges
        print('Drawing %d edges' % len(limited))
        for i, (u, v) in enumerate(limited): #edges: #[:10]:
            sys.stdout.write('%0.02f   \r' % (100. * i / len(limited)))
            sys.stdout.flush()
            a, b = coords[u], coords[v]
            ctx.set_source_rgba(0.5, 0.5, 0.5, 0.3)
            ctx.set_line_width(edge_w)
            draw_line(ctx, a[0], a[1], b[0], b[1])
        print('')

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    if isfile(output):
        print('Loading surface cache from %s' % output)
        img = cairo.ImageSurface.create_from_png(output)
        ctx.set_source_surface(img, 0, 0)
        ctx.paint()
    else:
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(-WIDTH, -HEIGHT, WIDTH*2, HEIGHT*2)
        ctx.fill()

    ctx.set_source_rgb(1, 1, 1)
    #ctx.scale(ratiow, ratiov)
    ctx.scale(scale * 0.95, scale * 0.95)
    #ctx.translate(tx * 0.9, ty * 0.9)
    ctx.translate(tx, ty)

    if not isfile(output):
        draw_vertices(ctx)
        draw_edges(ctx)

        print('Writing to %s' % output)
        surface.write_to_png(output)

    #i = 0
    #surface.write_to_png(output)
    #surface.write_to_png('frames/%06d.png' % i)
    #return

    if visited_filename:
        visited = set(read_visited(visited_filename))
        print('Drawing %d visited edges' % len(visited))
        for i, node in enumerate(visited):
            sys.stdout.write('%0.02f   \r' % (100. * i / len(visited)))
            sys.stdout.flush()
            x, y = coords[node]
            ctx.set_source_rgba(0.9, 0.1, 0.1, 0.7)
            ctx.set_line_width(visited_w)
            draw_circle(ctx, x, y, w, h)
            #surface.write_to_png('frames/%06d.png' % i)
            i += 1
            #if i > 10:
            #    break

        visited_output = dirname(output) + '/' + basename(output).rsplit('.', 1)[0] + '.visited.png'
        print('Writing visited to %s' % visited_output)
        surface.write_to_png(visited_output)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Helper that draws graphs from input files')
    parser.add_argument('--input', type=str,
                        help='Input graph filename')
    parser.add_argument('--visited', type=str,
                        help='Filename with visited vertices')
    parser.add_argument('--coords', type=str,
                        help='Filename with vertice coordinates')
    parser.add_argument('--output', type=str,
                        help='Output filename')
    parser.add_argument('--size', type=int, default=2000,
                        help='Width and height of the output image in pixels')

    return parser.parse_args()

def main():
    # input_graph = sys.argv[1]
    # visited = sys.argv[2]
    # coordinates = sys.argv[3]
    # output = sys.argv[4]
    #visited = sys.argv[2]

    args = parse_args()
    print(args)

    print('Drawing to %s' % args.output)
    #draw_graph_pillow(visited, coordinates, output)
    draw_graph_cairo(args.input,
                     args.visited,
                     args.coords,
                     args.output,
                     args.size)


if __name__ == '__main__':
    main()
