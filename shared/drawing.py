from dataclasses import dataclass
from PIL import ImageDraw
import colorsys


@dataclass
class Size:
    width: int
    height: int

    def values(self) -> tuple[int, int]:
        return (self.width, self.height)

@dataclass
class Point:
    x: int
    y: int

    def values(self) -> tuple[int, int]:
        return (self.x, self.y)


@dataclass
class Color:
    hue: int
    sat: int
    lum: int

    def as_rgb(self) -> tuple[int, int, int]:
        rgb_fractional = colorsys.hls_to_rgb(self.hue / 360, self.lum / 100, self.sat / 100)
        rgb = tuple(int(x * 255) for x in rgb_fractional)
        return rgb
    

    def mix(self, color: 'Color', ratio=0.5) -> 'Color':
        ratio = max(0, min(ratio, 1))
        
        # Handle the hue mixing with wraparound (circular value)
        h1, h2 = self.hue, color.hue
        if abs(h1 - h2) > 180:
            if h1 > h2:
                h2 += 360
            else:
                h1 += 360
        mixed_hue = (h1 * ratio + h2 * (1 - ratio)) % 360
        
        # Mix saturation and lightness linearly
        mixed_sat = self.sat * ratio + color.sat * (1 - ratio)
        mixed_lum = self.lum * ratio + color.lum * (1 - ratio)
        
        return Color(int(mixed_hue), int(mixed_sat), int(mixed_lum))


@dataclass
class Stroke:
    color: Color
    width: int


@dataclass
class Shape:
    size: Size
    fill: Color
    stroke: Stroke
    center: Point

    def draw(self, draw_function: callable):
        draw_function(
            self.diagonal_corners(),
            fill=self.fill.as_rgb(),
            outline=self.stroke.color.as_rgb(),
            width=self.stroke.width
        )

    def diagonal_corners(self):
        top_left_x = self.center.x - self.size.width / 2
        top_left_y = self.center.y - self.size.height / 2
        bottom_right_x = self.center.x + self.size.width / 2
        bottom_right_y = self.center.y + self.size.height / 2
        return [(top_left_x, top_left_y), (bottom_right_x, bottom_right_y)]


@dataclass
class Bounds:
    top_left: Point
    top_right: Point
    bottom_right: Point
    bottom_left: Point

    def values(self) -> list[tuple[int, int]]:
        return [
            self.top_left.values(),
            self.top_right.values(),
            self.bottom_right.values(),
            self.bottom_left.values(),
        ]


@dataclass
class Rectangle(Shape):
    def draw(self, canvas: ImageDraw):
        super().draw(canvas.rectangle)

    def bounds(self) -> Bounds:
        half_width = self.size.width // 2
        half_height = self.size.height // 2
        
        top_left = Point(self.center.x - half_width, self.center.y - half_height)
        top_right = Point(self.center.x + half_width, self.center.y - half_height)
        bottom_right = Point(self.center.x + half_width, self.center.y + half_height)
        bottom_left = Point(self.center.x - half_width, self.center.y + half_height)
        
        return Bounds(top_left, top_right, bottom_right, bottom_left)


@dataclass
class Ellipse(Shape):
    def draw(self, canvas: ImageDraw):
        super().draw(canvas.ellipse)

