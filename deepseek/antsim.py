import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Ant settings
ANT_SIZE = 5
ANT_SPEED = 2
SENSE_RANGE = 50

# Food settings
FOOD_SIZE = 10
FOOD_AMOUNT = 10

# Nest settings
NEST_SIZE = 20

class Ant:
    def __init__(self, x, y, nest):
        self.x = x
        self.y = y
        self.nest = nest
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False

    def move(self):
        if self.has_food:
            # If the ant has food, move directly toward the nest
            dx = self.nest.x - self.x
            dy = self.nest.y - self.y
            self.angle = math.atan2(dy, dx)
        else:
            # If the ant doesn't have food, wander randomly
            self.angle += random.uniform(-0.5, 0.5)  # Small random turn

        # Update position based on the angle
        self.x += ANT_SPEED * math.cos(self.angle)
        self.y += ANT_SPEED * math.sin(self.angle)

        # Bounce off walls
        if self.x < 0 or self.x > WIDTH:
            self.angle = math.pi - self.angle
        if self.y < 0 or self.y > HEIGHT:
            self.angle = -self.angle

    def sense_food(self, foods):
        if self.has_food:
            return None

        for food in foods:
            if food.amount <= 0:  # Ignore food that's already collected
                continue
            dx = food.x - self.x
            dy = food.y - self.y
            distance = math.hypot(dx, dy)
            if distance < SENSE_RANGE:
                self.angle = math.atan2(dy, dx)
                return food
        return None

    def check_collision(self, target_x, target_y, target_radius):
        # Check if the ant is touching the target (food or nest)
        distance = math.hypot(target_x - self.x, target_y - self.y)
        return distance < (ANT_SIZE + target_radius)

    def collect_food(self, food):
        if self.check_collision(food.x, food.y, FOOD_SIZE):
            self.has_food = True
            food.amount -= 1

    def deposit_food(self):
        if self.check_collision(self.nest.x, self.nest.y, NEST_SIZE):
            self.has_food = False

    def draw(self, screen):
        color = RED if self.has_food else BLACK
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ANT_SIZE)

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.amount = FOOD_SIZE

    def draw(self, screen):
        if self.amount > 0:  # Only draw food if it hasn't been fully collected
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.amount)

class Nest:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), NEST_SIZE)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ant Simulation")
    clock = pygame.time.Clock()

    nest = Nest(WIDTH // 2, HEIGHT // 2)
    ants = [Ant(random.randint(0, WIDTH), random.randint(0, HEIGHT), nest) for _ in range(20)]
    foods = [Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(FOOD_AMOUNT)]

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for ant in ants:
            ant.move()
            food = ant.sense_food(foods)
            if food and food.amount > 0:
                ant.collect_food(food)
            if ant.has_food:
                ant.deposit_food()

        for food in foods:
            food.draw(screen)

        for ant in ants:
            ant.draw(screen)

        nest.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()