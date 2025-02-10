import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions and setup (increased frame size)
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behaviors Simulation")
clock = pygame.time.Clock()

# Enhanced Color Palette
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GREEN = (46, 204, 113)
GRAY = (149, 165, 166)
BACKGROUND_TOP = (44, 62, 80)
BACKGROUND_BOTTOM = (52, 73, 94)
BUTTON_BASE = (127, 140, 141)
BUTTON_HOVER = (174, 182, 191)

# Helper functions
def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def normalize(vec):
    vec = pygame.Vector2(vec)  # Ensure vec is a Vector2
    length = vec.length()
    if length == 0:
        return pygame.Vector2(0, 0)
    return vec / length

# Enhanced Button class
class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.base_color = BUTTON_BASE
        self.hover_color = BUTTON_HOVER
        self.text_color = WHITE
        self.current_color = self.base_color
        self.font = pygame.font.Font(pygame.font.match_font('roboto'), 18)

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.current_color = self.hover_color
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.callback()
        else:
            self.current_color = self.base_color

# Agent class (unchanged)
class Agent:
    def __init__(self, x, y, color):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = 2
        self.color = color
        self.radius = 10

    def seek(self, target):
        desired = pygame.Vector2(target) - self.position
        desired = normalize(desired)
        desired *= self.max_speed
        self.velocity = desired

    def flee(self, target):
        desired = self.position - pygame.Vector2(target)
        desired = normalize(desired)
        desired *= self.max_speed
        self.velocity = desired

    def pursuit(self, target, target_velocity):
        future_position = pygame.Vector2(target) + pygame.Vector2(target_velocity) * 20
        self.seek(future_position)

    def evade(self, target, target_velocity):
        future_position = pygame.Vector2(target) + pygame.Vector2(target_velocity) * 20
        self.flee(future_position)

    def arrival(self, target):
        desired = pygame.Vector2(target) - self.position
        distance_to_target = desired.length()
        desired = normalize(desired)
        if distance_to_target < 100:
            desired *= self.max_speed * (distance_to_target / 100)
        else:
            desired *= self.max_speed
        self.velocity = desired

    def update(self):
        self.position += self.velocity
        self.position.x = max(self.radius, min(WIDTH - self.radius, self.position.x))
        self.position.y = max(self.radius, min(HEIGHT - self.radius, self.position.y))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        # Add subtle glow effect
        for i in range(3, 0, -1):
            pygame.draw.circle(screen, (*self.color, 50), (int(self.position.x), int(self.position.y)), self.radius + i, 1)

# Path class (unchanged)
class Path:
    def __init__(self, points):
        self.points = points
        self.current_index = 0
        self.direction = 1

    def get_next_point(self):
        return self.points[self.current_index]

    def advance(self, circuit=False, two_way=False):
        self.current_index += self.direction
        if self.current_index >= len(self.points):
            if circuit:
                self.current_index = 0
            elif two_way:
                self.current_index -= 2
                self.direction = -1
            else:
                self.current_index -= 1

        if self.current_index < 0 and two_way:
            self.current_index = 1
            self.direction = 1

# Create agents and path
agent = Agent(WIDTH // 4, HEIGHT // 4, BLUE)
path_points = [(100, 100), (700, 100), (700, 500), (100, 500)]
path = Path(path_points)

# Target agent (movable)
target = Agent(WIDTH // 2, HEIGHT // 2, RED)

# Behavior selection functions (unchanged)
def set_seek():
    global mode
    mode = "seek"

def set_flee():
    global mode
    mode = "flee"

def set_pursuit():
    global mode
    mode = "pursuit"

def set_evade():
    global mode
    mode = "evade"

def set_arrival():
    global mode
    mode = "arrival"

def set_circuit():
    global mode
    mode = "circuit"

def set_oneway():
    global mode
    mode = "oneway"

def set_twoway():
    global mode
    mode = "twoway"

# Create buttons
buttons = [
    Button(10, 200, 120, 45, "Seek", set_seek),
    Button(10, 250, 120, 45, "Flee", set_flee),
    Button(10, 300, 120, 45, "Pursuit", set_pursuit),
    Button(10, 350, 120, 45, "Evade", set_evade),
    Button(10, 400, 120, 45, "Arrival", set_arrival),
    Button(10, 450, 120, 45, "Circuit", set_circuit),
    Button(10, 500, 120, 45, "Oneway", set_oneway),
    Button(10, 550, 120, 45, "Twoway", set_twoway),
]

# Enhanced background gradient
def draw_custom_background(screen):
    for y in range(HEIGHT):
        r = int(BACKGROUND_TOP[0] + (BACKGROUND_BOTTOM[0] - BACKGROUND_TOP[0]) * y / HEIGHT)
        g = int(BACKGROUND_TOP[1] + (BACKGROUND_BOTTOM[1] - BACKGROUND_TOP[1]) * y / HEIGHT)
        b = int(BACKGROUND_TOP[2] + (BACKGROUND_BOTTOM[2] - BACKGROUND_TOP[2]) * y / HEIGHT)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

# Enhanced path rendering
def draw_path(screen, path):
    for i in range(len(path.points) - 1):
        pygame.draw.line(screen, GRAY, path.points[i], path.points[i + 1], 3)
    for point in path.points:
        pygame.draw.circle(screen, GREEN, point, 8)
    # Highlight the current target point with a pulsing effect
    current_point = path.get_next_point()
    pygame.draw.circle(screen, RED, current_point, 12 + int(math.sin(pygame.time.get_ticks() * 0.01) * 3))

# Main function (largely unchanged)
def main():
    global mode
    mode = "seek"  # Default behavior
    running = True
    dragging = False

    while running:
        draw_custom_background(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                target.position = pygame.Vector2(pygame.mouse.get_pos())

            for button in buttons:
                button.handle_event(event)

        # Behavior logic (unchanged)
        if mode == "seek":
            agent.seek(target.position)
        elif mode == "flee":
            agent.flee(target.position)
        elif mode == "pursuit":
            agent.pursuit(target.position, target.velocity)
        elif mode == "evade":
            agent.evade(target.position, target.velocity)
        elif mode == "arrival":
            agent.arrival(target.position)
        elif mode == "circuit":
            if distance(agent.position, path.get_next_point()) < 10:
                path.advance(circuit=True)
            agent.arrival(path.get_next_point())
        elif mode == "oneway":
            if distance(agent.position, path.get_next_point()) < 10:
                path.advance()
            agent.arrival(path.get_next_point())
        elif mode == "twoway":
            if distance(agent.position, path.get_next_point()) < 10:
                path.advance(two_way=True)
            agent.arrival(path.get_next_point())

        # Update and draw agents
        agent.update()
        target.draw(screen)
        agent.draw(screen)

        # Draw path
        draw_path(screen, path)

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()