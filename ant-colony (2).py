import pygame
import random
import numpy as np
from pygame.locals import *

# [Previous code for Button and Slider classes and constants remains exactly the same]

class AntColony:
    def __init__(self, num_ants=30):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ant Colony Simulation")
        
        # Controls
        self.paused = False
        self.play_pause_btn = Button(10, HEIGHT - 90, 100, 30, "Play/Pause")
        self.reset_btn = Button(120, HEIGHT - 90, 100, 30, "Reset")
        self.randomize_btn = Button(230, HEIGHT - 90, 100, 30, "Randomize")
        
        self.speed_slider = Slider(10, HEIGHT - 40, 200, 20, 0.1, 3.0, 1.0, "Speed")
        self.pheromone_weight_slider = Slider(220, HEIGHT - 40, 200, 20, 0.0, 1.0, 0.8, "Trail Follow")
        
        # Initialize base variables
        self.nest = (GRID_WIDTH//2, GRID_HEIGHT//2)
        # Separate pheromone grids for food and nest trails
        self.food_pheromone = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.home_pheromone = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food_sources = []
        
        # Initialize ants and food
        self.init_simulation(num_ants)
    
    def init_simulation(self, num_ants):
        self.food_pheromone = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.home_pheromone = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food_sources = []
        
        # Initialize ants
        self.ants = []
        for _ in range(num_ants):
            self.ants.append({
                'pos': self.nest,
                'has_food': False,
                'direction': random.uniform(0, 2*np.pi),
                'target': None,
                'last_food_pos': None
            })
        
        # Place food sources after ants are initialized
        self.place_food_sources()

    def get_pheromone_direction(self, x, y, pheromone_grid, radius=3):
        best_direction = None
        max_pheromone = 0
        
        # Check in a circle around the ant
        angles = np.linspace(0, 2*np.pi, 16, endpoint=False)
        for angle in angles:
            # Check at different distances
            for r in range(1, radius + 1):
                dx = r * np.cos(angle)
                dy = r * np.sin(angle)
                new_x = int(x + dx)
                new_y = int(y + dy)
                
                if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                    pheromone_val = pheromone_grid[new_x, new_y]
                    if pheromone_val > max_pheromone:
                        max_pheromone = pheromone_val
                        best_direction = angle
        
        return best_direction, max_pheromone

    def update_ant(self, ant):
        x, y = ant['pos']
        
        # If ant has food, head back to nest
        if ant['has_food']:
            dx = self.nest[0] - x
            dy = self.nest[1] - y
            distance_to_nest = np.sqrt(dx**2 + dy**2)
            
            # Drop food trail pheromone
            if ant['last_food_pos']:
                self.food_pheromone[int(x), int(y)] = min(5, self.food_pheromone[int(x), int(y)] + 
                                                         5 / (1 + distance_to_nest))
            
            # Head to nest
            if distance_to_nest < 2:
                ant['has_food'] = False
                ant['direction'] = random.uniform(0, 2*np.pi)
                ant['last_food_pos'] = None
            else:
                angle = np.arctan2(dy, dx)
                ant['direction'] = angle + random.uniform(-0.2, 0.2)
        
        # If ant doesn't have food, look for it
        else:
            # Check for food at current position
            if self.food[int(x), int(y)] > 0:
                # Find corresponding food source and reduce amount
                for source in self.food_sources:
                    sx, sy = source['pos']
                    if abs(sx - x) <= source['size'] and abs(sy - y) <= source['size']:
                        source['amount'] -= 1
                        if source['amount'] <= 0:
                            self.food_sources.remove(source)
                            self.place_food_source()
                        self.update_food_grid()
                        break
                ant['has_food'] = True
                ant['last_food_pos'] = (int(x), int(y))
                # Drop home trail pheromone
                self.home_pheromone[int(x), int(y)] = 5
                return
            
            # Follow food pheromone trail or random walk
            direction, strength = self.get_pheromone_direction(int(x), int(y), self.food_pheromone)
            
            if random.random() < self.pheromone_weight_slider.value and direction is not None:
                # Follow food pheromone trail
                ant['direction'] = direction + random.uniform(-0.1, 0.1)
            else:
                # Random walk with slight bias toward unexplored areas
                ant['direction'] += random.uniform(-0.3, 0.3)
        
        # Move ant
        speed = self.speed_slider.value
        new_x = x + speed * np.cos(ant['direction'])
        new_y = y + speed * np.sin(ant['direction'])
        
        # Bounce off edges
        if not (0 <= new_x < GRID_WIDTH):
            ant['direction'] = np.pi - ant['direction']
            new_x = max(0, min(GRID_WIDTH-1, new_x))
        if not (0 <= new_y < GRID_HEIGHT):
            ant['direction'] = -ant['direction']
            new_y = max(0, min(GRID_HEIGHT-1, new_y))
        
        ant['pos'] = (new_x, new_y)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_controls(event)
            
            if not self.paused:
                for ant in self.ants:
                    self.update_ant(ant)
                # Evaporate pheromones
                self.food_pheromone *= 0.995
                self.home_pheromone *= 0.995
            
            # Draw
            self.screen.fill(BLACK)
            
            # Draw pheromones (food trails in blue, home trails in green)
            pheromone_surface = pygame.Surface((WIDTH, HEIGHT - CONTROL_HEIGHT))
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    food_intensity = min(255, int(self.food_pheromone[x, y] * 50))
                    if food_intensity > 0:
                        pygame.draw.rect(pheromone_surface, (0, 0, food_intensity),
                                       (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
            self.screen.blit(pheromone_surface, (0, 0))
            
            # Draw food sources
            for source in self.food_sources:
                x, y = source['pos']
                size = source['size']
                intensity = int((source['amount'] / 100) * 255)
                color = (0, intensity, 0)
                pygame.draw.rect(self.screen, color,
                               ((x-size)*CELL_SIZE, (y-size)*CELL_SIZE,
                                size*2*CELL_SIZE, size*2*CELL_SIZE))
            
            # Draw nest
            pygame.draw.rect(self.screen, RED,
                           (self.nest[0]*CELL_SIZE-CELL_SIZE*2, 
                            self.nest[1]*CELL_SIZE-CELL_SIZE*2,
                            CELL_SIZE*4, CELL_SIZE*4))
            
            # Draw ants
            for ant in self.ants:
                color = BLUE if ant['has_food'] else WHITE
                x, y = ant['pos']
                pygame.draw.rect(self.screen, color,
                               (int(x*CELL_SIZE), int(y*CELL_SIZE), CELL_SIZE, CELL_SIZE))
            
            self.draw_controls()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

    # [Previous code for place_food_source, update_food_grid, place_food_sources, and handle_controls methods remains exactly the same]

if __name__ == "__main__":
    colony = AntColony(num_ants=30)
    colony.run()
