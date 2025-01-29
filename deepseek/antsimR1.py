import pygame
import numpy as np
import random
import math
from pygame.locals import *

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)
ANT_COLOR = (200, 200, 200)
FOOD_COLOR = (50, 200, 50)
NEST_COLOR = (200, 50, 50)
PHEROMONE_COLOR = (100, 100, 255)

NEST_POS = pygame.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
NEST_RADIUS = 20
ANT_COUNT = 100
ANT_SPEED = 2
SENSE_ANGLE = 30
SENSE_DISTANCE = 20
PHEROMONE_DECAY = 0.99
PHEROMONE_STRENGTH = 50
FOOD_AMOUNT = 500
FOOD_RADIUS = 10

class PheromoneGrid:
    def __init__(self):
        self.grid = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT), dtype=np.float32)
    
    def decay(self):
        self.grid *= PHEROMONE_DECAY
    
    def add_pheromone(self, x, y, amount):
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            self.grid[int(x)][int(y)] += amount
            self.grid[int(x)][int(y)] = min(self.grid[int(x)][int(y)], 500)

class FoodSource:
    def __init__(self, x, y, amount):
        self.pos = pygame.Vector2(x, y)
        self.amount = amount

class Ant:
    def __init__(self):
        self.pos = pygame.Vector2(NEST_POS)
        angle = random.uniform(0, 2*math.pi)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * ANT_SPEED
        self.state = "exploring"
        self.carried_food = 0
        self.max_food = 1
    
    def update(self, pheromone_grid, foods):
        if self.state == "exploring":
            self.explore(pheromone_grid)
            self.check_food(foods)
        elif self.state == "returning":
            self.return_to_nest(pheromone_grid)
            self.check_nest()
        
        self.pos += self.vel
        self.pos.x = max(0, min(SCREEN_WIDTH-1, self.pos.x))
        self.pos.y = max(0, min(SCREEN_HEIGHT-1, self.pos.y))
    
    def explore(self, pheromone_grid):
        best_strength = 0
        best_dir = None
        
        for angle in [-SENSE_ANGLE, 0, SENSE_ANGLE]:
            dir = self.vel.rotate(angle).normalize()
            sample_pos = self.pos + dir * SENSE_DISTANCE
            x = int(sample_pos.x)
            y = int(sample_pos.y)
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                strength = pheromone_grid.grid[x][y]
                if strength > best_strength:
                    best_strength = strength
                    best_dir = dir
        
        if best_dir is not None:
            self.vel = best_dir * ANT_SPEED
        else:
            self.vel = self.vel.rotate(random.uniform(-30, 30)).normalize() * ANT_SPEED
    
    def return_to_nest(self, pheromone_grid):
        direction = (NEST_POS - self.pos).normalize()
        self.vel = direction * ANT_SPEED
        pheromone_grid.add_pheromone(self.pos.x, self.pos.y, PHEROMONE_STRENGTH)
    
    def check_food(self, foods):
        for food in foods:
            if self.pos.distance_to(food.pos) < FOOD_RADIUS and food.amount > 0:
                self.carried_food = self.max_food
                self.state = "returning"
                food.amount -= 1
                return
    
    def check_nest(self):
        if self.pos.distance_to(NEST_POS) < NEST_RADIUS:
            self.carried_food = 0
            self.state = "exploring"

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    pheromone_grid = PheromoneGrid()
    ants = [Ant() for _ in range(ANT_COUNT)]
    foods = [FoodSource(SCREEN_WIDTH//4, SCREEN_HEIGHT//4, FOOD_AMOUNT),
             FoodSource(3*SCREEN_WIDTH//4, 3*SCREEN_HEIGHT//4, FOOD_AMOUNT)]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        pheromone_grid.decay()
        
        for ant in ants:
            ant.update(pheromone_grid, foods)
        
        screen.fill(BACKGROUND_COLOR)
        
        # Draw pheromones
        pheromone_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                strength = pheromone_grid.grid[x][y]
                if strength > 0:
                    alpha = min(int(strength * 2), 100)
                    pheromone_surface.set_at((x, y), (*PHEROMONE_COLOR, alpha))
        screen.blit(pheromone_surface, (0, 0))
        
        # Draw nest
        pygame.draw.circle(screen, NEST_COLOR, NEST_POS, NEST_RADIUS)
        
        # Draw food
        for food in foods:
            if food.amount > 0:
                pygame.draw.circle(screen, FOOD_COLOR, food.pos, FOOD_RADIUS)
        
        # Draw ants
        for ant in ants:
            pygame.draw.circle(screen, ANT_COLOR, (int(ant.pos.x), int(ant.pos.y)), 2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()