import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import random

class AntSimulation:
    def __init__(self, width=100, height=100, num_ants=50, num_food_sources=5):
        # Environment dimensions
        self.width = width
        self.height = height
        
        # Initialize grid layers
        self.food_grid = np.zeros((height, width))
        self.home_pheromone = np.zeros((height, width))
        self.food_pheromone = np.zeros((height, width))
        
        # Create nest at the center
        self.nest_x = width // 2
        self.nest_y = height // 2
        
        # Place food sources randomly
        self.place_food(num_food_sources)
        
        # Create ants
        self.ants = []
        for _ in range(num_ants):
            self.ants.append({
                'x': self.nest_x,
                'y': self.nest_y,
                'has_food': False,
                'direction': random.uniform(0, 2 * np.pi),
                'steps_from_nest': 0
            })
        
        # Simulation parameters
        self.pheromone_evaporation_rate = 0.05
        self.pheromone_deposit_amount = 1.0
        self.direction_change_probability = 0.2
        self.random_direction_weight = 0.3
        self.pheromone_direction_weight = 0.7
        
    def place_food(self, num_food_sources):
        """Place food sources randomly in the environment"""
        for _ in range(num_food_sources):
            # Keep food away from the nest
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                distance_from_nest = np.sqrt((x - self.nest_x)**2 + (y - self.nest_y)**2)
                
                # Food should be some distance away from the nest
                if distance_from_nest > self.width / 4:
                    break
            
            # Create a food patch
            food_size = random.randint(5, 15)
            for i in range(-food_size // 2, food_size // 2):
                for j in range(-food_size // 2, food_size // 2):
                    if (0 <= x + i < self.width) and (0 <= y + j < self.height):
                        self.food_grid[y + j, x + i] = 5
    
    def update(self):
        """Update the simulation by one time step"""
        # Move each ant
        for ant in self.ants:
            self.move_ant(ant)
        
        # Evaporate pheromones
        self.home_pheromone *= (1 - self.pheromone_evaporation_rate)
        self.food_pheromone *= (1 - self.pheromone_evaporation_rate)
    
    def move_ant(self, ant):
        """Move an ant based on its current state"""
        x, y = ant['x'], ant['y']
        
        # Check if ant is at nest and has food
        if ant['has_food'] and self.is_at_nest(ant):
            ant['has_food'] = False
            ant['direction'] = (ant['direction'] + np.pi) % (2 * np.pi)  # Turn around
            ant['steps_from_nest'] = 0
            return
        
        # Check if ant finds food
        if not ant['has_food'] and self.food_grid[int(y), int(x)] > 0:
            self.food_grid[int(y), int(x)] -= 1
            ant['has_food'] = True
            ant['direction'] = (ant['direction'] + np.pi) % (2 * np.pi)  # Turn around
            return
        
        # Deposit pheromones
        if ant['has_food']:
            self.food_pheromone[int(y), int(x)] += self.pheromone_deposit_amount
        else:
            self.home_pheromone[int(y), int(x)] += self.pheromone_deposit_amount
        
        # Update direction based on pheromones
        if random.random() < self.direction_change_probability:
            if ant['has_food']:
                # Follow home pheromones
                new_direction = self.get_pheromone_direction(ant, self.home_pheromone)
            else:
                # Follow food pheromones
                new_direction = self.get_pheromone_direction(ant, self.food_pheromone)
            
            random_direction = random.uniform(0, 2 * np.pi)
            
            # Combine random and pheromone directions
            ant['direction'] = (self.random_direction_weight * random_direction + 
                               self.pheromone_direction_weight * new_direction) % (2 * np.pi)
        
        # Calculate new position
        new_x = x + np.cos(ant['direction'])
        new_y = y + np.sin(ant['direction'])
        
        # Boundary handling (wrap around)
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            ant['direction'] = random.uniform(0, 2 * np.pi)
            new_x = max(0, min(self.width - 1, new_x))
            new_y = max(0, min(self.height - 1, new_y))
        
        # Update position
        ant['x'] = new_x
        ant['y'] = new_y
        
        # Update steps from nest
        if not ant['has_food']:
            ant['steps_from_nest'] += 1
        
        # If an ant wanders too far without food, direct it back to the nest
        if not ant['has_food'] and ant['steps_from_nest'] > 100:
            # Start heading back to the nest
            direction_to_nest = np.arctan2(self.nest_y - y, self.nest_x - x)
            ant['direction'] = direction_to_nest
    
    def get_pheromone_direction(self, ant, pheromone_grid):
        """Determine direction based on surrounding pheromones"""
        x, y = int(ant['x']), int(ant['y'])
        max_pheromone = 0
        best_direction = ant['direction']
        
        # Check pheromone levels in 8 surrounding cells
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx, ny = (x + i) % self.width, (y + j) % self.height
                
                if pheromone_grid[ny, nx] > max_pheromone:
                    max_pheromone = pheromone_grid[ny, nx]
                    best_direction = np.arctan2(j, i)
        
        return best_direction
    
    def is_at_nest(self, ant):
        """Check if an ant is at or near the nest"""
        dist = np.sqrt((ant['x'] - self.nest_x)**2 + (ant['y'] - self.nest_y)**2)
        return dist < 2
    
    def render(self):
        """Render the current state for visualization"""
        # Create a combined grid for visualization
        viz_grid = np.zeros((self.height, self.width))
        
        # Add food
        viz_grid[self.food_grid > 0] = 1
        
        # Add pheromones (normalized)
        normalized_food_pheromone = np.clip(self.food_pheromone / 5, 0, 1) * 0.3
        normalized_home_pheromone = np.clip(self.home_pheromone / 5, 0, 1) * 0.5
        
        viz_grid[normalized_food_pheromone > 0.05] = 2
        viz_grid[normalized_home_pheromone > 0.05] = 3
        
        # Add nest
        nest_radius = 3
        for i in range(-nest_radius, nest_radius + 1):
            for j in range(-nest_radius, nest_radius + 1):
                nx, ny = self.nest_x + i, self.nest_y + j
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    viz_grid[ny, nx] = 4
        
        # Add ants
        for ant in self.ants:
            x, y = int(ant['x']), int(ant['y'])
            if 0 <= x < self.width and 0 <= y < self.height:
                viz_grid[y, x] = 5 if ant['has_food'] else 6
        
        return viz_grid

    def count_food_collected(self):
        """Count how much food has been collected"""
        # Count initial food amount vs current food amount
        initial_food = 5 * 5 * 15 * 5  # approx based on placement method
        current_food = np.sum(self.food_grid)
        return initial_food - current_food


# Simulation and visualization
def run_simulation(num_steps=500, display_interval=10):
    # Create simulation
    sim = AntSimulation(width=80, height=80, num_ants=100, num_food_sources=3)
    
    # Create figure for animation
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Custom colormap: black, green, blue, red, yellow, white, gray
    cmap = ListedColormap(['black', 'green', 'blue', 'red', 'yellow', 'white', 'gray'])
    
    # Initialize plot
    img = ax.imshow(sim.render(), cmap=cmap, vmin=0, vmax=6)
    ax.set_title('Ant Colony Simulation - Step 0')
    plt.colorbar(img, ticks=[0, 1, 2, 3, 4, 5, 6], 
                 label='0: Empty, 1: Food, 2: Food Pheromone, 3: Home Pheromone, 4: Nest, 5: Ant with Food, 6: Foraging Ant')
    
    food_collected_text = ax.text(0.02, 0.95, f'Food Collected: 0', transform=ax.transAxes, color='white')
    
    # Animation update function
    def update(frame):
        for _ in range(display_interval):
            sim.update()
        
        img.set_array(sim.render())
        ax.set_title(f'Ant Colony Simulation - Step {frame * display_interval}')
        
        food_collected = sim.count_food_collected()
        food_collected_text.set_text(f'Food Collected: {food_collected:.1f}')
        
        return img, food_collected_text
    
    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=num_steps//display_interval, 
                                 interval=100, blit=True)
    
    plt.tight_layout()
    plt.show()
    
    return ani

if __name__ == "__main__":
    ani = run_simulation(num_steps=2000, display_interval=5)