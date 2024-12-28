import pygame
import random
import numpy as np
from pygame.locals import *

# [Previous code for Button and Slider classes remains exactly the same until AntColony class]

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
        self.pheromone = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food_sources = []
        
        # Initialize ants and food
        self.init_simulation(num_ants)
    
    def init_simulation(self, num_ants):
        self.pheromone = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food = np.zeros((GRID_WIDTH, GRID_HEIGHT))
        self.food_sources = []
        
        # Initialize ants
        self.ants = []
        for _ in range(num_ants):
            self.ants.append({
                'pos': self.nest,
                'has_food': False,
                'direction': random.uniform(0, 2*np.pi),
                'target': None
            })
        
        # Place food sources after ants are initialized
        self.place_food_sources()

    # [Rest of the code remains exactly the same]

if __name__ == "__main__":
    colony = AntColony(num_ants=30)
    colony.run()
