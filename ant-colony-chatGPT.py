import pygame
import random
import math

# Initialize pygame
pygame.init()

# Set up screen size
screen_width = 800
screen_height = 600
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
ANT_SPEED = 2
ANT_VISION = 50

# Food parameters
FOOD_SIZE = 10

# Nest position
NEST_X = screen_width // 2
NEST_Y = screen_height // 2

# Create an Ant class
class Ant:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.carrying_food = False

	def move(self):
		if self.carrying_food:
			# Move toward the nest when carrying food
			self.return_to_nest()
		else:
			# Move randomly when not carrying food
			angle = random.uniform(0, 2 * math.pi)
			self.x += ANT_SPEED * math.cos(angle)
			self.y += ANT_SPEED * math.sin(angle)
			
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
				self.x += ANT_SPEED * math.cos(angle)
				self.y += ANT_SPEED * math.sin(angle)

				# If the ant reaches the food, pick it up
				if closest_distance < ANT_SIZE + FOOD_SIZE:
					self.carrying_food = True
					foods.remove(closest_food)

	def return_to_nest(self):
		# Move toward the nest when carrying food
		angle = math.atan2(NEST_Y - self.y, NEST_X - self.x)
		self.x += ANT_SPEED * math.cos(angle)
		self.y += ANT_SPEED * math.sin(angle)

		# If the ant reaches the nest, drop the food
		if math.hypot(self.x - NEST_X, self.y - NEST_Y) < ANT_SIZE + FOOD_SIZE:
			self.carrying_food = False

	def draw(self):
		pygame.draw.circle(screen, RED if not self.carrying_food else GREEN, (int(self.x), int(self.y)), ANT_SIZE)

# Create a Food class
class Food:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def draw(self):
		pygame.draw.circle(screen, BROWN, (self.x, self.y), FOOD_SIZE)

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

	# Draw food
	for food in foods:
		food.draw()

	# Draw the nest
	pygame.draw.circle(screen, GREEN, (NEST_X, NEST_Y), 20)

	# Update the display
	pygame.display.flip()

	# Cap the frame rate
	clock.tick(30)

# Quit pygame
pygame.quit()
