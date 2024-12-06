from PIL import Image, ImageDraw
import math

# Create a new image with a black background
WIDTH = 480
HEIGHT = 480
CENTER = WIDTH // 2

# Create image and drawing context
img = Image.new('RGB', (WIDTH, HEIGHT), 'black')
draw = ImageDraw.Draw(img)

# Colors
TACTICAL_BLUE = (0, 74, 255)  # RGB equivalent of 0x004aff
DIM_BLUE = (0, 37, 127)      # Darker blue for secondary elements

def draw_circle(x, y, r, color, width=1):
    draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=width)

def draw_arc(center_x, center_y, radius, start_angle, end_angle, color, width=1):
    bbox = (center_x-radius, center_y-radius, center_x+radius, center_y+radius)
    draw.arc(bbox, start_angle, end_angle, fill=color, width=width)

# Draw main crosshairs
draw.line((CENTER, 0, CENTER, HEIGHT), fill=TACTICAL_BLUE, width=2)
draw.line((0, CENTER, WIDTH, CENTER), fill=TACTICAL_BLUE, width=2)

# Draw central circles
draw_circle(CENTER, CENTER, 206, TACTICAL_BLUE, 3)
draw_circle(CENTER, CENTER, 30, TACTICAL_BLUE, 2)

# Draw tactical arcs
arcs = [
    (300, 380, 60),
    (300, 380, 60),
    (55, 240, 60),
    (55, 90, 90),
    (180, 380, 90)
]

for start_angle, end_angle, radius in arcs:
    for r in range(radius-3, radius+4):
        draw_arc(CENTER, CENTER, r, start_angle, end_angle, TACTICAL_BLUE)

# Draw angle lines
angles = [55, 15, 345, 295, 240, 200]
line_length = 134

for angle in angles:
    radians = math.radians(angle)
    end_x = CENTER + int(line_length * math.cos(radians))
    end_y = CENTER + int(line_length * math.sin(radians))
    draw.line((CENTER, CENTER, end_x, end_y), fill=TACTICAL_BLUE, width=2)

# Draw targeting reticle (45-degree rotation)
reticle_size = 50
angle = math.radians(45)
c = math.cos(angle)
s = math.sin(angle)
center_x = CENTER
center_y = CENTER - 40  # Offset up from center

# Draw reticle lines
draw.line((center_x - reticle_size*c, center_y - reticle_size*s,
           center_x + reticle_size*c, center_y + reticle_size*s),
          fill=TACTICAL_BLUE, width=2)
draw.line((center_x - reticle_size*s, center_y + reticle_size*c,
           center_x + reticle_size*s, center_y - reticle_size*c),
          fill=TACTICAL_BLUE, width=2)

# Draw reticle circles
draw_circle(center_x, center_y, reticle_size, TACTICAL_BLUE, 2)
draw_circle(center_x, center_y, reticle_size-15, TACTICAL_BLUE, 1)
draw_circle(center_x, center_y, reticle_size-30, TACTICAL_BLUE, 1)

# Add some "detected objects" as rectangles
objects = [
    (CENTER-50, CENTER-50, 20, 8, 55),
    (CENTER+40, CENTER-65, 10, 6, 112),
    (CENTER+75, CENTER-40, 6, 7, 150),
    (CENTER+55, CENTER+60, 14, 4, 238)
]

for x, y, w, h, angle in objects:
    # Draw a small rectangle for each object
    radians = math.radians(angle)
    c = math.cos(radians)
    s = math.sin(radians)
    
    points = [
        (x - w/2*c - h/2*s, y - w/2*s + h/2*c),
        (x + w/2*c - h/2*s, y + w/2*s + h/2*c),
        (x + w/2*c + h/2*s, y + w/2*s - h/2*c),
        (x - w/2*c + h/2*s, y - w/2*s - h/2*c)
    ]
    
    draw.polygon(points, outline=TACTICAL_BLUE)

# Save the image
img.save('tactical_display_preview.png')
