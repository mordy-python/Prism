from . import utils
import colorsys
import gizeh
import hashlib
import io
from PIL import Image
import pkg_resources
import random
from typing import List, Tuple


class Color:
    """ Represents an RGB color.
    """
    def __init__(self, red: int = 0, green: int = 0, blue: int = 0):
        self.red: int = red
        self.green: int = green
        self.blue: int = blue

    def __repr__(self):
        red, green, blue = self.rgb()
        return f'<Color ({red:1.2f}, {green:1.2f}, {blue:1.2f})>'

    def __eq__(self, value):
        if isinstance(value, Color):
            return (self.red, self.green, self.blue) \
                    == (value.red, value.green, value.blue)
        return False

    def hsv(self) -> Tuple[float]:
        """ Get color as HSV.
        """
        return colorsys.rgb_to_hsv(*self.rgb())

    def rgb(self) -> Tuple[float]:
        """ Get color as RGB.
        """
        return tuple(
            (channel / 255 for channel in (self.red, self.green, self.blue))
        )

    def rotate_hue(self, degrees: int) -> 'Color':
        """ Creates a copy of a color with its hue rotated.

            :param degrees: Amount in degrees to rotate the hue wheel.
            :returns: Resulting Color.
        """
        hue, saturation, value = self.hsv()
        hue = (((hue * 360) + degrees) % 360) / 360
        return Color.from_hsv(hue, saturation, value)

    @classmethod
    def from_hsv(cls, hue: float, saturation: float, value: float) -> 'Color':
        """ Constructs a new Color from HSV values.
        """
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return cls.from_rgb(*rgb)

    @classmethod
    def from_rgb(cls, red: float, green: float, blue: float) -> 'Color':
        """ Constructs a new Color from RGB values.
        """
        rgb_255 = [int(channel * 255) for channel in (red, green, blue)]
        return cls(*rgb_255)


class Crabatar:
    """ Represents a single avatar/user.
    """
    patterns = [utils.draw_horizontal_lines, utils.draw_vertical_lines,
                utils.draw_angled_lines, utils.draw_wavy_lines,
                utils.draw_recessed_circles, utils.draw_recessed_triangles,
                utils.draw_overlapping_circles]
    crab_img = Image.open(
        pkg_resources.resource_filename(__name__, 'crab.png')
    )

    def __init__(self, username: str):
        self.username: str = username
        self.hash: str = hashlib.sha256(self.username.encode())
        self.random = random.Random()
        self.reseed()

    def __repr__(self):
        return f'<Crabatar {self.username!r}>'

    def reseed(self):
        """ Resets random number generator.
        """
        self.random.seed(self.hash.digest()[-20:])

    def generate_pattern(self, size=512) -> gizeh.Surface:
        """ Creates a colored pattern unique to this Crabatar.

            :param size: Pixel width of resulting surface.
            :returns: Generated surface.
        """
        self.reseed()

        res = 10000000
        hue = self.random.randrange(res) / res
        saturation = self.random.randrange(0.4 * res, 0.6 * res) / res
        palette = Palette(Color.from_hsv(hue, saturation, 1))
        pattern_func = self.random.choice(Crabatar.patterns)
        pattern = pattern_func(size, palette)
        return pattern

    def make_avatar(self, size=512, inverted=False):
        """ Creates an avatar image unique to this Crabatar.

            :param size: Pixel width of resulting image.
            :param inverted: Swaps colored and white sections of avatar.
            :returns: Avatar as a Pillow Image
        """
        pattern = self.generate_pattern(size)
        pattern = Image.fromarray(pattern.get_npimage())
        if inverted:
            white_background = gizeh.Surface(width=size, height=size,
                                             bg_color=(1, 1, 1))
            white_background = Image.fromarray(white_background.get_npimage())
            white_background.paste(pattern, (0, 0), Crabatar.crab_img)
            return white_background
        else:
            pattern.paste(Crabatar.crab_img, (0, 0), Crabatar.crab_img)
            return pattern

    def get_avatar_bytes(self, format: str = 'PNG', size=512, inverted=False):
        """ Creates an avatar image unique to this Crabatar and encodes it in
            an image format.

            :param format: Image format to use. (See `Pillow.Image.save`)
            :param size: Pixel width of resulting image.
            :param inverted: Swaps colored and white sections of avatar.
            :returns: The image file bytes
        """
        avatar = self.make_avatar(size=size, inverted=inverted)
        avatar_bytes = io.BytesIO()
        avatar.save(avatar_bytes, format)
        return avatar_bytes

    def write_avatar(self, filename: str, format: str = 'PNG', size=512,
                     inverted=False):
        """ Creates an avatar image unique to this Crabatar and writes it to an
            image file.

            :param filename: The filename to write to.
            :param format: Image format to use. (See `Pillow.Image.save`)
            :param size: Pixel width of resulting image.
            :param inverted: Swaps colored and white sections of avatar.
        """
        avatar = self.make_avatar(size=size, inverted=inverted)
        avatar.save(filename, format)


class Palette:
    """ Handles creation of color palettes from a root color.
    """
    def __init__(self, root: 'Color'):
        self.root: 'Color' = root

    def analogous(self, count: int, split_degrees: int) -> List[Tuple[float]]:
        """ Creates an analogous palette.

            :param count: Number of colors to generate.
            :param split_degrees: Width in degrees of analogous colors' hues.
            :returns: Colors as RGB values.
        """
        colors = list()
        for i in range(count):
            colors.append(self.root.rotate_hue(
                (split_degrees // count) * i - (split_degrees // 2)
            ).rgb())
        return colors

    def complimentary(self) -> List[Tuple[float]]:
        """ Creates a complimentary palette.

            :returns: Colors as RGB values.
        """
        return [
            self.root.rgb(),
            self.root.rotate_hue(180).rgb()
        ]

    def monochromatic(self, count: int) -> List[Tuple[float]]:
        """ Creates a monochromatic palette.

            :param count: Number of colors to generate.
            :returns: Colors as RGB values.
        """
        h, s, v = self.root.hsv()
        return [Color.from_hsv(h, s - (idx / 10), v).rgb()
                for idx in range(count)]

    def regular(self, count: int) -> List[Tuple[float]]:
        """ Creates a palette of colors evenly spaced around the hue wheel.

            :param count: Number of colors to generate.
            :returns: Colors as RGB values.
        """
        colors = list()
        for i in range(count):
            colors.append(self.root.rotate_hue((360 // count) * i).rgb())
        return colors

    def split_complimentary(self, split_degrees: int = 30) \
            -> List[Tuple[float]]:
        """ Creates a split-complimentary palette.

            :param split_degrees: Width in degrees of complimentary colors'
                hues.
            :returns: Colors as RGB values.
        """
        return [
            self.root.rgb(),
            self.root.rotate_hue(180 - split_degrees // 2).rgb(),
            self.root.rotate_hue(180 + split_degrees // 2).rgb()
        ]

    def tetradic(self, split_degrees: int = 60) -> List[Tuple[float]]:
        """ Creates a tetradic palette.

            :param split_degrees: Width in degrees of palette colors' hues.
            :returns: Colors as RGB values.
        """
        return [
            self.root.rgb(),
            self.root.rotate_hue(split_degrees).rgb(),
            self.root.rotate_hue(180).rgb(),
            self.root.rotate_hue(split_degrees + 180).rgb()
        ]

    def triad(self) -> List[Tuple[float]]:
        """ Creates a triad palette.

            :returns: Colors as RGB values.
        """
        return self.regular(3)

    @classmethod
    def from_hash(cls, hash: hashlib._hashlib.HASH, saturation: float = 0.5,
                  value: float = 1) -> 'Palette':
        """ Creates a color palette based on a SHA-256 hash.
        """
        hue = hash.digest()[0] % 256 / 255
        root_color = Color.from_hsv(hue, saturation, value)
        return cls(root=root_color)
