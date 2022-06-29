from . import models
import gizeh
import math


def jsin(x: int, length: int) -> int:
    """ A sin-like mathematical function for integer oscillations.

        :param x: Current horizontal position in the oscillation.
        :param l: Length of oscillation.
        :returns: Vertical position in the oscillation.
    """
    return ((x // length) * (length - 1)) \
        - ((x % length) * (-1 + (x // length) * 2))


def draw_overlapping_circles(size: int, palette: 'models.Palette',
                             count: int = 4) -> gizeh.Surface:
    """ Draws layers of circles.

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of rows and circles per row.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(2)
    surface = gizeh.Surface(width=size, height=size)
    for v_idx in range(count):
        for idx in range(count):
            color = colors[(idx + v_idx) % len(colors)]
            x_pos = idx * (size // (count - 1))
            y_pos = v_idx * (size // (count - 1))
            color_circle = gizeh.circle(
                r=size // count,
                xy=(x_pos, y_pos),
                fill=color
            )
            color_circle.draw(surface)
    return surface


def draw_recessed_circles(size: int, palette: 'models.Palette',
                          count: int = 5) -> gizeh.Surface:
    """ Draws circles recessing into each other.

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of circles to generate.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(count)
    colors.reverse()
    surface = gizeh.Surface(width=size, height=size)
    for idx in range(count):
        color = colors[idx % len(colors)]
        color_circle = gizeh.circle(
            r=size - ((size / count) * idx),
            xy=(size // 2, size // 2),
            fill=color
        )
        color_circle.draw(surface)
    return surface


def draw_recessed_triangles(size: int, palette: 'models.Palette',
                            count: int = 4) -> gizeh.Surface:
    """ Draws triangles recessing into each other.

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of triangles to generate.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(count)
    colors.reverse()
    surface = gizeh.Surface(width=size, height=size, bg_color=(1, 1, 1))
    radius = int(size * 1.5)
    for idx in range(count):
        color = colors[idx % len(colors)]
        color_triangle = gizeh.regular_polygon(
            r=radius - ((radius / count) * idx),
            n=3,
            angle=math.pi * 1.5,
            xy=(size // 2, size // 2 + (math.pi * size) / 10),
            fill=color
        )
        color_triangle.draw(surface)
    return surface


def draw_angled_lines(size: int, palette: 'models.Palette', count: int = 5) \
        -> gizeh.Surface:
    """ Draws series of lines at a 45-degree angle

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of lines.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(2)
    surface = gizeh.Surface(width=size, height=size)
    for idx in range(count + 2):
        idx = idx - 1
        color = colors[idx % len(colors)]
        color_rect = gizeh.rectangle(
            lx=size * 2,
            ly=size / (count - 1) + 2,
            xy=(size / 2, (size / (count - 1)) * idx),
            fill=color
        ).rotate(45, center=(size // 2, size // 2))
        color_rect.draw(surface)
    return surface


def draw_horizontal_lines(size: int, palette: 'models.Palette',
                          count: int = 7) -> gizeh.Surface:
    """ Draws series of horizontal lines.

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of lines.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(2)
    surface = gizeh.Surface(width=size, height=size)
    for idx in range(count):
        color = colors[idx % len(colors)]
        color_rect = gizeh.rectangle(
            lx=size,
            ly=size / count + 1,
            xy=(size / 2, (size / count) * idx + (size / (count * 2))),
            fill=color
        )
        color_rect.draw(surface)
    return surface


def draw_vertical_lines(size: int, palette: 'models.Palette', count: int = 7) \
        -> gizeh.Surface:
    """ Draws series of vertical lines.

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of lines.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(2)
    surface = gizeh.Surface(width=size, height=size)
    for idx in range(count):
        color = colors[idx % len(colors)]
        color_rect = gizeh.rectangle(
            lx=size / count + 1,
            ly=size,
            xy=((size / count) * idx + (size / (count * 2)), size / 2),
            fill=color
        )
        color_rect.draw(surface)
    return surface


def draw_wavy_lines(size: int, palette: 'models.Palette', count: int = 7,
                    frequency: int = 6) -> gizeh.Surface:
    """ Draws series of wavy vertical lines.

        :param size: Width and height of resulting surface.
        :param palette: The color palette to source colors from.
        :param count: Number of lines.
        :param frequency: Frequency of waves per line.
        :returns: Resulting surface.
    """
    colors = palette.monochromatic(2)
    surface = gizeh.Surface(width=size, height=size)

    for idx in range(count + 1):
        color = colors[idx % len(colors)]
        points = [
            (
                # Px
                ((
                    ((p + p // (frequency + 2)) % 2) / 2 \
                    + idx + (p // (frequency + 2))
                ) - 1) * (size / (count - 1)) \
                + (-1 + (p // (frequency + 2)) * 2),
                # Py
                (jsin(p, frequency + 2) - 1) * (size / (frequency - 1))
            )
            for p in range((frequency + 2) * 2)
        ]
        line = gizeh.polyline(points=points, fill=color)
        line.draw(surface)
    return surface
