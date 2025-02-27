import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import random
from collections import deque

class AntSimulation:
    def __init__(self, width=100, height=100, n_ants=50, n_food_sources=5, 
                 evaporation_rate=0.05, diffusion_rate=0.1, food_amount=100):
        # Environment setup
        self.width = width
        self.height = height
        self.n_ants = n_ants
        self.n_food_sources = n_food_sources
        self.evaporation_rate = evaporation_rate
        self.diffusion_rate = diffusion_rate
        self.food_amount = food_amount
        
        # Initialize grids
        self.grid = np.zeros((height, width), dtype=int)  # 0: empty, 1: nest, 2: food, 3: ant
        self.pheromone_home = np.zeros((height, width))
        self.pheromone_food = np.zeros((height, width))
        self.food_grid = np.zeros((height, width), dtype=int)
        
        # Initialize ants
        self.ants = []
        
        # Initialize nest position (center of grid)
        self.nest_pos = (height // 2, width // 2)
        self.grid[self.nest_pos] = 1
        
        # Place food sources
        self.place_food_sources()
        
        # Create ants
        self.create_ants()
        
        # Statistics
        self.food_collected = 0
        self.steps = 0
    
    def place_food_sources(self):
        """Place food sources randomly on the grid"""
        for _ in range(self.n_food_sources):
            # Place food away from the nest
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                # Make sure it's at least 20% of grid size away from nest
                min_distance = min(self.width, self.height) * 0.2
                if self.distance((y, x), self.nest_pos) > min_distance and self.grid[y, x] == 0:
                    break
            
            # Create a small cluster of food
            for i in range(-2, 3):
                for j in range(-2, 3):
                    ny, nx = y + i, x + j
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        if random.random() < 0.7:  # 70% chance to place food in this cell
                            self.grid[ny, nx] = 2
                            self.food_grid[ny, nx] = self.food_amount
    
    def create_ants(self):
        """Create ants at the nest position"""
        for i in range(self.n_ants):
            self.ants.append({
                'id': i,
                'pos': self.nest_pos,
                'has_food': False,
                'direction': random.choice([(0, 1), (1, 0), (0, -1), (-1, 0),
                                          (1, 1), (1, -1), (-1, 1), (-1, -1)]),
                'state': 'exploring'  # exploring, returning, following_food, following_home
            })
    
    def distance(self, pos1, pos2):
        """Calculate Euclidean distance between two positions"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_neighbors(self, pos):
        """Get all valid neighboring positions"""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                ny, nx = pos[0] + dy, pos[1] + dx
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    neighbors.append((ny, nx))
        return neighbors
    
    def update_pheromones(self):
        """Update pheromone levels - evaporation and diffusion"""
        # Evaporation
        self.pheromone_food *= (1 - self.evaporation_rate)
        self.pheromone_home *= (1 - self.evaporation_rate)
        
        # Diffusion - simple average with neighbors
        if self.diffusion_rate > 0:
            pheromone_food_new = self.pheromone_food.copy()
            pheromone_home_new = self.pheromone_home.copy()
            
            for y in range(self.height):
                for x in range(self.width):
                    neighbors = self.get_neighbors((y, x))
                    if neighbors:
                        # Food pheromone diffusion
                        neighbor_sum = sum(self.pheromone_food[ny, nx] for ny, nx in neighbors)
                        avg = neighbor_sum / len(neighbors)
                        pheromone_food_new[y, x] = (1 - self.diffusion_rate) * self.pheromone_food[y, x] + self.diffusion_rate * avg
                        
                        # Home pheromone diffusion
                        neighbor_sum = sum(self.pheromone_home[ny, nx] for ny, nx in neighbors)
                        avg = neighbor_sum / len(neighbors)
                        pheromone_home_new[y, x] = (1 - self.diffusion_rate) * self.pheromone_home[y, x] + self.diffusion_rate * avg
            
            self.pheromone_food = pheromone_food_new
            self.pheromone_home = pheromone_home_new
    
    def move_ant(self, ant):
        """Move a single ant based on its state and surroundings"""
        y, x = ant['pos']
        neighbors = self.get_neighbors((y, x))
        
        # If at nest and has food, drop it
        if ant['pos'] == self.nest_pos and ant['has_food']:
            ant['has_food'] = False
            self.food_collected += 1
            ant['state'] = 'exploring'
        
        # If at food source and doesn't have food, pick it up
        elif self.grid[y, x] == 2 and not ant['has_food'] and self.food_grid[y, x] > 0:
            ant['has_food'] = True
            self.food_grid[y, x] -= 1
            if self.food_grid[y, x] <= 0:
                self.grid[y, x] = 0  # Remove food source when depleted
            ant['state'] = 'returning'
            # Drop food pheromone when finding food
            self.pheromone_food[y, x] = 1.0
        
        # Decide next direction based on state
        next_pos = None
        if ant['has_food']:  # Returning to nest
            # Drop food pheromone
            self.pheromone_food[y, x] = max(self.pheromone_food[y, x], 0.5)
            
            # First priority: follow home pheromone if strong enough
            home_pheromones = [(self.pheromone_home[ny, nx], (ny, nx)) for ny, nx in neighbors]
            strong_pheromones = [pos for level, pos in home_pheromones if level > 0.2]
            
            if strong_pheromones and random.random() < 0.8:  # 80% chance to follow pheromone
                next_pos = max(home_pheromones)[1]
                ant['state'] = 'following_home'
            else:
                # Otherwise, try to move towards nest
                distances = [(self.distance((ny, nx), self.nest_pos), (ny, nx)) for ny, nx in neighbors]
                next_pos = min(distances)[1]
                ant['state'] = 'returning'
        
        else:  # Looking for food
            # Drop home pheromone
            self.pheromone_home[y, x] = max(self.pheromone_home[y, x], 0.5)
            
            # First check for food in neighbors
            food_neighbors = [(ny, nx) for ny, nx in neighbors if self.grid[ny, nx] == 2]
            if food_neighbors:
                next_pos = random.choice(food_neighbors)
            else:
                # Follow food pheromone if strong enough
                food_pheromones = [(self.pheromone_food[ny, nx], (ny, nx)) for ny, nx in neighbors]
                strong_pheromones = [pos for level, pos in food_pheromones if level > 0.1]
                
                if strong_pheromones and random.random() < 0.7:  # 70% chance to follow pheromone
                    next_pos = max(food_pheromones)[1]
                    ant['state'] = 'following_food'
                else:
                    # Random walk with some momentum
                    if random.random() < 0.7:  # 70% chance to continue in same direction
                        dy, dx = ant['direction']
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            next_pos = (ny, nx)
                        else:
                            next_pos = random.choice(neighbors)
                            # Update direction
                            ant['direction'] = (next_pos[0] - y, next_pos[1] - x)
                    else:
                        next_pos = random.choice(neighbors)
                        # Update direction
                        ant['direction'] = (next_pos[0] - y, next_pos[1] - x)
                    
                    ant['state'] = 'exploring'
        
        # Update ant position
        if next_pos:
            ant['pos'] = next_pos
            # Update direction for momentum
            ant['direction'] = (next_pos[0] - y, next_pos[1] - x)
    
    def step(self):
        """Advance the simulation by one time step"""
        # Clear ants from grid for visualization
        ant_positions = []
        for ant in self.ants:
            if self.grid[ant['pos']] == 3:  # Only clear if it's an ant (not nest or food)
                self.grid[ant['pos']] = 0
            ant_positions.append(ant['pos'])
        
        # Move each ant
        for ant in self.ants:
            self.move_ant(ant)
        
        # Update pheromones
        self.update_pheromones()
        
        # Update ants on grid for visualization
        for ant in self.ants:
            if self.grid[ant['pos']] == 0:  # Only place ant if cell is empty
                self.grid[ant['pos']] = 3
        
        self.steps += 1
        
        # Return statistics
        return {
            'food_collected': self.food_collected,
            'steps': self.steps
        }
    
    def run(self, n_steps=100):
        """Run the simulation for n steps"""
        stats = []
        for _ in range(n_steps):
            stat = self.step()
            stats.append(stat)
        return stats
    
    def visualize(self, ax=None):
        """Visualize the current state of the simulation"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create a visualization grid
        vis_grid = self.grid.copy()
        
        # Create a custom colormap
        colors = ['white', 'brown', 'green', 'black']  # empty, nest, food, ant
        cmap = ListedColormap(colors)
        
        # Plot the grid
        ax.imshow(vis_grid, cmap=cmap, vmin=0, vmax=3)
        
        # Plot pheromones as transparent overlays
        food_pheromone = np.ma.masked_where(self.pheromone_food < 0.05, self.pheromone_food)
        home_pheromone = np.ma.masked_where(self.pheromone_home < 0.05, self.pheromone_home)
        
        ax.imshow(food_pheromone, cmap='Reds', alpha=0.5, vmin=0, vmax=1)
        ax.imshow(home_pheromone, cmap='Blues', alpha=0.5, vmin=0, vmax=1)
        
        ax.set_title(f'Step: {self.steps}, Food Collected: {self.food_collected}')
        ax.axis('off')
        
        return ax

# Run the simulation
def run_ant_simulation(width=80, height=80, n_ants=50, n_steps=200):
    """Run the ant simulation and create an animation"""
    simulation = AntSimulation(width=width, height=height, n_ants=n_ants)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    def update(frame):
        ax.clear()
        simulation.step()
        simulation.visualize(ax)
        return ax,
    
    ani = animation.FuncAnimation(fig, update, frames=n_steps, interval=100, blit=False)
    plt.close()  # Prevent duplicate display in notebooks
    
    return simulation, ani

# Use this to run the simulation without animation
def run_and_plot(width=80, height=80, n_ants=50, n_steps=50, plot_interval=10):
    """Run the simulation and plot at specified intervals"""
    simulation = AntSimulation(width=width, height=height, n_ants=n_ants)
    
    # Plot initial state
    plt.figure(figsize=(10, 10))
    simulation.visualize()
    plt.title('Initial State')
    plt.show()
    
    # Run and plot at intervals
    for i in range(0, n_steps, plot_interval):
        for _ in range(plot_interval):
            simulation.step()
        
        plt.figure(figsize=(10, 10))
        simulation.visualize()
        plt.title(f'Step {simulation.steps}')
        plt.show()
    
    # Final stats
    print(f"Simulation completed after {simulation.steps} steps")
    print(f"Total food collected: {simulation.food_collected}")
    
    return simulation

# Example usage
if __name__ == "__main__":
    # For static snapshots
    simulation = run_and_plot(width=50, height=50, n_ants=30, n_steps=100, plot_interval=25)
    
    # If you want animation, uncomment below (works better in Jupyter notebooks)
    simulation, ani = run_ant_simulation(width=50, height=50, n_ants=30, n_steps=100)
    from IPython.display import HTML
    HTML(ani.to_jshtml())