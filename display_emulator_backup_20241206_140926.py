import pygame
import math
import sys
import time
import random
from pygame import gfxdraw
import os

# Initialize Pygame
pygame.init()

# Display settings
WIDTH = 480
HEIGHT = 480
CENTER = (WIDTH // 2, HEIGHT // 2)

# Create the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ESP32 Star Wars Tactical Display")

# Load Aurebesh font
FONT_SIZE = 28
font_paths = ["Aurebesh.otf", "Aurebesh Condensed.otf"]

FONT = None
for font_path in font_paths:
    try:
        font_path = os.path.join(os.path.dirname(__file__), font_path)
        if os.path.exists(font_path):
            FONT = pygame.font.Font(font_path, FONT_SIZE)
            print(f"Loaded font: {font_path}")
            break
    except Exception as e:
        print(f"Failed to load font {font_path}: {e}")
        continue

if FONT is None:
    print("No Aurebesh font found, using default font")
    FONT = pygame.font.Font(None, FONT_SIZE)

# Colors
TACTICAL_BLUE = (0, 74, 255)  # COLOR_TACTICAL_BLUE from Arduino code
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 200, 0)
RED = (255, 0, 0)

# Tactical Objects (converted from Arduino arrays)
ARCS = [
    # Inner arcs following circle curvature
    # Format: (start_angle, end_angle, radius, thickness, should_blink)
    (30, 90, 60, 0, True),      # Upper right quadrant, blinking
    (100, 150, 60, 0, False),   # Upper right quadrant
    (190, 240, 60, 0, True),    # Lower right quadrant, blinking
    (260, 310, 60, 0, False),   # Lower left quadrant
    (330, 20, 60, 0, True),     # Upper left quadrant, blinking
    
    # Middle layer arcs
    (45, 85, 90, 0, False),     # Upper right
    
    # Outer arcs
    (180, 380, 45, 0, False),   # Original outer arc
    (200, 380, 30, 0, False),   # Original outer arc
    (200, 380, 30, 0, False)    # Original outer arc
]

ANGLE_LINES = [
    # Format: (start_x, start_y, length, angle)
    # Increased lengths from 85 to 100
    (CENTER[0] + 16, CENTER[1] + 18, 100, 55),
    (CENTER[0] + 21, CENTER[1] + 9, 100, 15),
    (CENTER[0] + 21, CENTER[1] - 9, 100, 345),
    (CENTER[0] + 12, CENTER[1] - 18, 100, 295),
    (CENTER[0] - 12, CENTER[1] - 18, 100, 240),
    (CENTER[0] - 19, CENTER[1] - 9, 100, 200)
]

class BlinkingObject:
    def __init__(self, x, y, w, h, angle):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = angle
        self.visible = True
        self.last_blink = time.time()
        self.blink_interval = random.uniform(1.5, 3.0)
        self.should_blink = random.random() < 0.3
        self.next_blink_check = time.time() + random.uniform(2.0, 5.0)
        self.can_turn_red = random.random() < 0.15  # About 2 objects will be selected
        self.current_color = RED if self.can_turn_red else WHITE  # Red-capable objects are never white
        self.red_mode = self.can_turn_red  # Start in red mode if capable
        self.red_duration = time.time() + random.uniform(4.0, 6.0) if self.can_turn_red else 0
        self.red_blink_interval = 0.5  # Faster blink rate for red warnings

    def update(self):
        current_time = time.time()
        
        # Periodically reassign which objects are blinking
        if current_time > self.next_blink_check:
            self.should_blink = random.random() < 0.3
            self.next_blink_check = current_time + random.uniform(2.0, 5.0)
        
        # Only update if this object is currently set to blink
        if self.should_blink:
            current_interval = self.red_blink_interval if self.red_mode else self.blink_interval
            
            if current_time - self.last_blink > current_interval:
                self.visible = not self.visible
                
                # Handle red warning objects
                if self.can_turn_red:
                    if current_time > self.red_duration:
                        # Reset duration for next red phase
                        self.red_duration = current_time + random.uniform(4.0, 6.0)
                    self.current_color = RED  # Always stay red
                
                self.last_blink = current_time
                if not self.red_mode:
                    self.blink_interval = random.uniform(1.5, 3.0)
        else:
            self.visible = True
            if self.can_turn_red:
                self.current_color = RED  # Always stay red

class BlinkingArc:
    def __init__(self):
        self.last_blink = time.time()
        self.visible = True
        self.blink_interval = random.uniform(0.3, 0.8)
    
    def update(self):
        current_time = time.time()
        if current_time - self.last_blink > self.blink_interval:
            self.visible = not self.visible
            self.last_blink = current_time
            self.blink_interval = random.uniform(0.3, 0.8)

blinking_arcs = []

def draw_line_at_angle(x, y, length, angle, color):
    radians = math.radians(angle)
    end_x = x + length * math.cos(radians)
    end_y = y + length * math.sin(radians)
    
    # Draw thicker lines (3 pixels)
    for offset in range(3):
        offset_x = offset - 1
        offset_y = offset - 1
        pygame.draw.line(screen, color, 
                        (x + offset_x, y + offset_y), 
                        (end_x + offset_x, end_y + offset_y), 1)

def draw_arc(start_angle, end_angle, radius, color):
    rect = pygame.Rect(CENTER[0] - radius, CENTER[1] - radius, radius * 2, radius * 2)
    pygame.draw.arc(screen, color, rect, math.radians(start_angle), math.radians(end_angle), 1)

def draw_rect_at_angle(cx, cy, w, h, angle, color):
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, (0, 0, w, h))
    rotated = pygame.transform.rotate(surface, -angle)
    screen.blit(rotated, (cx - rotated.get_width()//2, cy - rotated.get_height()//2))

def draw_static_elements():
    # Draw main circle - much thicker
    radius = min(WIDTH, HEIGHT)//2 - 20
    for i in range(15):
        pygame.draw.circle(screen, TACTICAL_BLUE, CENTER, radius - i, 1)
    
    # Draw center circle
    center_radius = 30
    for i in range(3):
        pygame.draw.circle(screen, TACTICAL_BLUE, CENTER, center_radius - i, 1)
    
    # Draw crosshairs
    for i in range(3):  # Draw 3 parallel lines for thickness
        offset = i - 1
        pygame.draw.line(screen, TACTICAL_BLUE, (CENTER[0] - 240 + offset, CENTER[1] + offset), (CENTER[0] + 240 + offset, CENTER[1] + offset), 1)
        pygame.draw.line(screen, TACTICAL_BLUE, (CENTER[0] + offset, CENTER[1] - 240 + offset), (CENTER[0] + offset, CENTER[1] + 240 + offset), 1)
    
    # Draw tactical arcs
    blink_index = 0
    for start_angle, end_angle, radius, rotation, should_blink in ARCS:
        if not should_blink or (should_blink and blinking_arcs[blink_index].visible):
            rect = pygame.Rect(CENTER[0] - radius, CENTER[1] - radius, radius * 2, radius * 2)
            # Draw thicker arcs (3 pixels)
            for i in range(3):
                r = radius + i - 1
                rect = pygame.Rect(CENTER[0] - r, CENTER[1] - r, r * 2, r * 2)
                pygame.draw.arc(screen, TACTICAL_BLUE, rect, math.radians(start_angle), math.radians(end_angle), 1)
        if should_blink:
            blink_index += 1
    
    # Draw angle lines
    for x, y, length, angle in ANGLE_LINES:
        draw_line_at_angle(x, y, length, angle, TACTICAL_BLUE)

def draw_detected_objects():
    # More objects, positioned further from center, avoiding text area
    objects = [
        # Top left quadrant
        (CENTER[0] - 100, CENTER[1] - 120, 60, 12, 55),
        (CENTER[0] - 85, CENTER[1] - 130, 25, 8, 60),  # Made smaller
        (CENTER[0] - 70, CENTER[1] - 140, 50, 15, 65),
        # Top quadrant
        (CENTER[0] - 20, CENTER[1] - 150, 30, 8, 90),  # Made smaller
        (CENTER[0], CENTER[1] - 160, 65, 10, 90),
        (CENTER[0] + 20, CENTER[1] - 155, 20, 8, 90),  # Made smaller
        # Top right quadrant
        (CENTER[0] + 80, CENTER[1] - 130, 55, 12, 120),
        (CENTER[0] + 100, CENTER[1] - 120, 25, 8, 125),  # Made smaller
        (CENTER[0] + 120, CENTER[1] - 100, 50, 15, 130),
        # Right quadrant
        (CENTER[0] + 150, CENTER[1] - 20, 65, 12, 180),
        (CENTER[0] + 160, CENTER[1], 20, 8, 180),  # Made smaller
        (CENTER[0] + 155, CENTER[1] + 20, 50, 15, 180),
        # Upper right side
        (CENTER[0] + 120, CENTER[1] + 100, 55, 12, 230),
        (CENTER[0] + 100, CENTER[1] + 120, 30, 8, 235),  # Made smaller
        (CENTER[0] + 80, CENTER[1] + 130, 50, 15, 240),
        # Top area
        (CENTER[0] + 20, CENTER[1] - 155, 25, 8, 270),  # Made smaller
        (CENTER[0], CENTER[1] - 160, 45, 10, 270),
        (CENTER[0] - 20, CENTER[1] - 150, 50, 15, 270),
    ]
    
    return [BlinkingObject(x, y, w, h, angle) for x, y, w, h, angle in objects]

class TextDisplay:
    def __init__(self):
        # Two different sets of words to alternate between
        self.text_sets = [
            ["ALERT", "CAUTION", "SCAN", "ACTIVE"],
            ["SYSTEM", "TARGET", "LOCK", "READY"],
        ]
        self.current_set = 0  # Which set of words we're currently displaying
        self.current_text_idx = 0
        self.current_char_idx = 0
        self.display_start_time = None
        self.last_char_time = time.time()
        self.char_delay = 0.1
        self.word_delay = 0.3
        self.display_duration = 10.0
        self.is_typing = True
        self.is_displaying = False
        self.is_clearing = False
        self.displayed_texts = ["", "", "", ""]

    def update(self):
        current_time = time.time()
        
        # Typing phase
        if self.is_typing:
            if current_time - self.last_char_time > (self.word_delay if self.current_char_idx == 0 else self.char_delay):
                current_word = self.text_sets[self.current_set][self.current_text_idx]
                if self.current_char_idx < len(current_word):
                    self.displayed_texts[self.current_text_idx] = current_word[:self.current_char_idx + 1]
                    self.current_char_idx += 1
                    self.last_char_time = current_time
                else:
                    self.current_char_idx = 0
                    self.current_text_idx += 1
                    if self.current_text_idx >= len(self.text_sets[0]):
                        self.is_typing = False
                        self.is_displaying = True
                        self.display_start_time = current_time
        
        # Display complete phase
        elif self.is_displaying:
            if current_time - self.display_start_time > self.display_duration:
                self.is_displaying = False
                self.is_clearing = True
        
        # Clearing phase
        elif self.is_clearing:
            self.displayed_texts = ["", "", "", ""]
            self.current_text_idx = 0
            self.is_clearing = False
            self.is_typing = True
            # Switch to next set of words
            self.current_set = (self.current_set + 1) % len(self.text_sets)
            
    def draw(self, screen):
        # Adjusted text position further left to avoid center line
        start_x = CENTER[0] - 170  # Moved more left from -150
        start_y = CENTER[1] + 45   # Keeping same vertical position
        
        for i, text in enumerate(self.displayed_texts):
            if text:  # Only render non-empty strings
                text_surface = FONT.render(text, True, YELLOW)
                text_rect = text_surface.get_rect()
                text_rect.left = start_x + (i * 15)  # Keeping same diagonal movement
                text_rect.top = start_y + (i * 28)   # Keeping same vertical spacing
                screen.blit(text_surface, text_rect)

def main():
    global blinking_arcs
    
    clock = pygame.time.Clock()
    running = True
    
    # Initialize blinking arcs
    blinking_arcs = [BlinkingArc() for arc in ARCS if arc[4]]
    
    # Create blinking objects
    blinking_objects = draw_detected_objects()
    
    # Create text display
    text_display = TextDisplay()
    
    # Boot sequence
    screen.fill(BLACK)
    pygame.display.flip()
    time.sleep(0.5)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(BLACK)
        draw_static_elements()
        
        # Update and draw blinking objects
        for obj in blinking_objects:
            obj.update()
            if obj.visible:
                draw_rect_at_angle(obj.x, obj.y, obj.w, obj.h, obj.angle, obj.current_color)
        
        # Update blinking arcs
        for arc in blinking_arcs:
            arc.update()
        
        # Update and draw text
        text_display.update()
        text_display.draw(screen)
        
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
