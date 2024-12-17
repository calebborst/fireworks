import pygame
import random
import math
import threading

# ========================= SETTINGS =========================
# Window Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS_LIMIT = 60

# Firework Settings
FIREWORK_FREQUENCY = 0.04  # Probability of creating a new firework each frame
FIREWORK_MIN_HEIGHT = WINDOW_HEIGHT // 20  # Minimum height fireworks will explode
FIREWORK_MAX_HEIGHT = WINDOW_HEIGHT // 3  # Maximum height fireworks will explode
FIREWORK_SPEED_MIN = 6  # Minimum upward velocity
FIREWORK_SPEED_MAX = 8  # Maximum upward velocity
HORIZONTAL_DRIFT = 0.7  # Max horizontal drift while rising

# Explosion Settings
EXPLOSION_PARTICLE_COUNT = 40  # Number of particles per explosion
EXPLOSION_SPEED_MIN = 1  # Minimum particle speed
EXPLOSION_SPEED_MAX = 2  # Maximum particle speed
GRAVITY = 0.05  # Gravity applied to particles
PARTICLE_SIZE = 2  # Size of explosion particles
FIREWORK_SIZE = 2  # Size of the firework as it rises

# Colors
BACKGROUND_COLOR = (0, 0, 0)  # Black background
FPS_TEXT_COLOR = (255, 255, 255)  # White for FPS text

# ===========================================================


pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Realistic Fireworks")

clock = pygame.time.Clock()

pygame.font.init()
fps_font = pygame.font.SysFont("Arial", 18)


DECELERATION = 0.98  # Linear slowdown factor (slightly less than 1)
FADE_RATE = 3  # Rate at which particles fade out gradually
FLASH_DURATION = 5  # Shorter duration of the flash effect in frames
FLASH_RADIUS = 30  # Reduced flash radius

pygame.mixer.init()
POP_SOUND = pygame.mixer.Sound("pop.mp3")

class Firework:
    def __init__(self, color, firework_type):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT
        self.color = color
        self.firework_type = firework_type
        self.time_to_explode = random.randint(90, 130)
        self.vel_y = -random.uniform(FIREWORK_SPEED_MIN, FIREWORK_SPEED_MAX)
        self.vel_x = random.uniform(-HORIZONTAL_DRIFT, HORIZONTAL_DRIFT)
        self.particles = []
        self.exploded = False
        self.flash_timer = 0

    def explode(self):
        """Trigger the explosion with particles."""
        self.exploded = True
        self.flash_timer = FLASH_DURATION
        POP_SOUND.play()
        if self.firework_type == "standard":
            self.standard_explosion()

    def standard_explosion(self):
        """Create particles for a standard explosion."""
        for _ in range(EXPLOSION_PARTICLE_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            alpha = 255
            self.particles.append([self.x, self.y, dx, dy, alpha])

    def update(self):
        """Update the firework's state."""
        if not self.exploded:
            self.y += self.vel_y
            self.x += self.vel_x
            self.vel_y += GRAVITY
            if self.y <= FIREWORK_MIN_HEIGHT or self.time_to_explode <= 0:
                self.explode()
            self.time_to_explode -= 1
        else:
            if self.flash_timer > 0:
                self.flash_timer -= 1

            for particle in self.particles[:]:
                particle[0] += particle[2]
                particle[1] += particle[3]
                particle[3] += GRAVITY

                particle[2] *= DECELERATION
                particle[3] *= DECELERATION

                particle[4] = max(0, particle[4] - FADE_RATE)

                if particle[4] == 0:
                    self.particles.remove(particle)

    def draw(self):
        """Draw the firework, explosion flash, or its particles."""
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), FIREWORK_SIZE)
        else:
            if self.flash_timer > 0:
                flash_alpha = int(128 * (self.flash_timer / FLASH_DURATION))
                flash_surface = pygame.Surface((FLASH_RADIUS * 2, FLASH_RADIUS * 2), pygame.SRCALPHA)
                for y in range(FLASH_RADIUS * 2):
                    for x in range(FLASH_RADIUS * 2):
                        dx = x - FLASH_RADIUS
                        dy = y - FLASH_RADIUS
                        distance = math.sqrt(dx**2 + dy**2)
                        if distance <= FLASH_RADIUS:
                            gradient_alpha = int(flash_alpha * (1 - distance / FLASH_RADIUS))
                            flash_surface.set_at((x, y), (*self.color[:3], gradient_alpha))
                screen.blit(flash_surface, (int(self.x - FLASH_RADIUS), int(self.y - FLASH_RADIUS)))

            for particle in self.particles:
                if particle[4] > 0:
                    faded_color = (*self.color[:3], int(particle[4]))
                    surface = pygame.Surface((PARTICLE_SIZE * 2, PARTICLE_SIZE * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surface, faded_color, (PARTICLE_SIZE, PARTICLE_SIZE), PARTICLE_SIZE)
                    screen.blit(surface, (int(particle[0] - PARTICLE_SIZE), int(particle[1] - PARTICLE_SIZE)))



fireworks = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    if random.random() < FIREWORK_FREQUENCY:
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        fireworks.append(Firework(color, "standard"))

    for firework in fireworks[:]:
        firework.update()
        firework.draw()
        if firework.exploded and len(firework.particles) == 0:
            fireworks.remove(firework)

    fps_text = fps_font.render(f"FPS: {int(clock.get_fps())}", True, FPS_TEXT_COLOR)
    screen.blit(fps_text, (WINDOW_WIDTH - 80, 10))

    pygame.display.flip()
    clock.tick(FPS_LIMIT)

pygame.quit()
