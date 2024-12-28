import pygame
import random
import math

# Initialize pygame
pygame.init()

# Set up screen size
screen_width = 1200  # Increased grid size
screen_height = 800  # Increased grid size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ant Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)

# Ant parameters
ANT_SIZE = 5
ANT_SPEED = 5
ANT_VISION = 50
TURN_RATE = 5 # How much the ant changes direction each time
HEADING_NOISE = 0.5  # Small randomness in direction for smoother movement

# Food parameters
FOOD_SIZE = 10
BIG_FOOD_SIZE = 30  # Larger food size for bigger food sources
HUGE_FOOD_SIZE = 80  # Huge food size for very big food sources

# Nest position
NEST_X = screen_width // 2
NEST_Y = screen_height // 2

# Create an Ant class
class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.carrying_food = False
        self.heading = random.uniform(0, 2 * math.pi)  # Random starting direction

    def move(self):
        if self.carrying_food:
            # Move toward the nest when carrying food
            self.return_to_nest()
        else:
            # Move randomly when not carrying food, but with gradual turns
            self.heading += random.uniform(-HEADING_NOISE, HEADING_NOISE)  # Gradual change in direction
            self.x += ANT_SPEED * math.cos(self.heading)
            self.y += ANT_SPEED * math.sin(self.heading)
        
        # Stay within screen boundaries
        self.x = max(0, min(self.x, screen_width))
        self.y = max(0, min(self.y, screen_height))

    def find_food(self, foods):
        if not self.carrying_food:
            closest_food = None
            closest_distance = ANT_VISION

            # Look for the closest food within vision range
            for food in foods:
                dist = math.hypot(food.x - self.x, food.y - self.y)
                if dist < closest_distance:
                    closest_food = food
                    closest_distance = dist

            # If a food is found within vision range, move toward it
            if closest_food:
                angle = math.atan2(closest_food.y - self.y, closest_food.x - self.x)
                self.heading = angle  # Update heading to move toward food
                self.x += ANT_SPEED * math.cos(self.heading)
                self.y += ANT_SPEED * math.sin(self.heading)

                # If the ant reaches the food, pick it up
                if closest_distance < ANT_SIZE + FOOD_SIZE:
                    self.carrying_food = True
                    foods.remove(closest_food)
                    # Respawn a new food item randomly
                    spawn_food(foods)

    def return_to_nest(self):
        # Move toward the nest when carrying food
        angle = math.atan2(NEST_Y - self.y, NEST_X - self.x)
        self.heading = angle  # Update heading to move toward the nest
        self.x += ANT_SPEED * math.cos(self.heading)
        self.y += ANT_SPEED * math.sin(self.heading)

        # If the ant reaches the nest, drop the food
        if math.hypot(self.x - NEST_X, self.y - NEST_Y) < ANT_SIZE + FOOD_SIZE:
            self.carrying_food = False

    def draw(self):
        pygame.draw.circle(screen, RED if not self.carrying_food else GREEN, (int(self.x), int(self.y)), ANT_SIZE)

# Create a Food class
class Food:
    def __init__(self, x, y, size=FOOD_SIZE):
        self.x = x
        self.y = y
        self.total_size = size  # The total size of the food, determines how many bites it will take
        self.remaining_size = size  # The current remaining size of the food
        self.decrement_size = 1  # Amount by which the size decreases per pickup

    def draw(self):
        pygame.draw.circle(screen, BROWN, (self.x, self.y), int(self.remaining_size))

    def reduce_size(self):
        # Decrease the remaining size by the decrement amount
        self.remaining_size -= self.decrement_size
        if self.remaining_size <= 0:
            self.remaining_size = 0

    def is_empty(self):
        return self.remaining_size <= 0

# Function to spawn a new food source
def spawn_food(foods):
    # Randomly spawn food on the grid
    food_choice = random.choice([FOOD_SIZE, BIG_FOOD_SIZE, HUGE_FOOD_SIZE])
    new_food = Food(random.randint(50, screen_width-50), random.randint(50, screen_height-50), food_choice)
    foods.append(new_food)

# Initialize ants and food
ants = [Ant(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(10)]
foods = [Food(random.randint(100, screen_width-100), random.randint(100, screen_height-100)) for _ in range(5)]

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move ants and perform tasks
    for ant in ants:
        if ant.carrying_food:
            ant.return_to_nest()
        else:
            ant.find_food(foods)
            ant.move()
        
        ant.draw()

    # Remove empty food sources
    foods = [food for food in foods if not food.is_empty()]

    # Draw food
    for food in foods:
        food.draw()

    # Make ants reduce food size gradually when picking up
    for food in foods:
        if food.is_empty():
            foods.remove(food)

    # Draw the nest
    pygame.draw.circle(screen, GREEN, (NEST_X, NEST_Y), 20)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

# Quit pygame
pygame.quit()
