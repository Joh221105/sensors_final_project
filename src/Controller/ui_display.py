import displayio
import math

def polar(cx, cy, r, a):
    """converts x,y distance from center, radius, and angle to calculate x,y coordinates to place pixel"""
    rad = math.radians(a)
    return int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad))


# sets white as only color reference, saves memory
_shared_palette = None

def _get_shared_palette():
    global _shared_palette
    if _shared_palette is None:
        _shared_palette = displayio.Palette(1)
        _shared_palette[0] = 0xFFFFFF
    return _shared_palette


def make_pixel(x, y):
    """Create a single white pixel"""
    bmp = displayio.Bitmap(1, 1, 1)
    pal = _get_shared_palette()
    return displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)


# calculate once to see where the large circle would be placed
_circle_positions = None

def _get_circle_positions():
    global _circle_positions
    if _circle_positions is None:
        cx, cy = 64, 38
        radius = 22
        _circle_positions = []
        for a in range(0, 360, 4):
            x, y = polar(cx, cy, radius, a)
            _circle_positions.append((x, y))
    return _circle_positions


def draw_circle_and_arc(bg_group, start, end):
    """draw the central circular and success zone arc"""
    cx, cy = 64, 40
    radius = 22
    
    # clear screen
    while len(bg_group) > 0:
        bg_group.pop()
    
    # draw circle
    for x, y in _get_circle_positions():
        bg_group.append(make_pixel(x, y))
    
    # draw arc
    if start < end:
        angles = range(start, end, 3)
    else:
        angles = list(range(start, 360, 3)) + list(range(0, end, 3))
    
    for r in (radius, radius - 1):
        for a in angles:
            x, y = polar(cx, cy, r, a)
            bg_group.append(make_pixel(x, y))


def build_cursor(fg_group):
    """define the cursor sprite shape"""
    pattern = [
        "0001000",
        "0011100",
        "0111110",
        "1111111",
        "0111110",
        "0011100",
        "0001000",
        "0001000",
        "0001000",
    ]
    h = len(pattern)
    w = len(pattern[0])
    bmp = displayio.Bitmap(w, h, 2)
    pal = displayio.Palette(2)
    pal[0] = 0x000000
    pal[1] = 0xFFFFFF
    pal.make_transparent(0)
    
    for y in range(h):
        for x in range(w):
            if pattern[y][x] == "1":
                bmp[x, y] = 1
    
    cursor = displayio.TileGrid(bmp, pixel_shader=pal)
    fg_group.append(cursor)
    return cursor


def update_cursor_rotation(cursor, angle):
    """update cursor position based on angle as it moves along the circle"""
    cx, cy = 64, 38
    r = 16
    x, y = polar(cx, cy, r, angle)
    cursor.x = x - 3
    cursor.y = y - 3
