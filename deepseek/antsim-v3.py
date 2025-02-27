import pygame
import random
import math
from collections import deque

# Constants
WIDTH, HEIGHT = 1200, 900  # Increased map size
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)  # New gray color
COUNTER_BG_COLOR = (0, 0, 0, 128)  # Semi-transparent black background
COUNTER_BORDER_COLOR = (255, 255, 255)  # White border
BUTTON_BG_COLOR = (50, 50, 50)  # Dark gray for buttons
BUTTON_TEXT_COLOR = (255, 255, 255)  # White text for buttons

# Ant settings
ANT_SIZE = 5
ANT_SPEED = 2  # Initial ant speed
SENSE_RANGE = 100  # Increased sensing range

# Food settings
FOOD_SIZE = 10
FOOD_AMOUNT = 10

# Nest settings
NEST_SIZE = 20
FOOD_TO_SPAWN_ANT = 5  # Food units required to spawn a new ant

# Pheromone settings
PHEROMONE_STRENGTH = 200  # Increased from 100
PHEROMONE_DECAY = 0.5     # Reduced from 1
PHEROMONE_DROP_INTERVAL = 10

class Pheromone:
    def __init__(self, x, y, strength, direction):
        self.x = x
        self.y = y
        self.strength = strength
        self.direction = direction  # "to_nest" or "to_food"

    def decay(self):
        self.strength -= PHEROMONE_DECAY
        return self.strength > 0

    def draw(self, screen):
        if self.direction == "to_nest":
            color = (255, 255, 0, int(self.strength / PHEROMONE_STRENGTH * 255))  # Yellow for "to_nest"
        else:
            color = (255, 165, 0, int(self.strength / PHEROMONE_STRENGTH * 255))  # Orange for "to_food"
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)

class Ant:
    def __init__(self, x, y, nest, speed):
        self.x = x
        self.y = y
        self.nest = nest
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False
        self.pheromone_timer = 0
        self.speed = speed

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
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

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

    def sense_pheromones(self, pheromones, pheromone_influence):
        if self.has_food:
            return None

        strongest_pheromone = None
        max_strength = 0

        for pheromone in pheromones:
            if pheromone.direction != "to_food":  # Only follow "to_food" pheromones
                continue
            dx = pheromone.x - self.x
            dy = pheromone.y - self.y
            distance = math.hypot(dx, dy)
            if distance < SENSE_RANGE and pheromone.strength > max_strength:
                strongest_pheromone = pheromone
                max_strength = pheromone.strength

        if strongest_pheromone:
            # Adjust the angle significantly toward the pheromone
            target_angle = math.atan2(strongest_pheromone.y - self.y, strongest_pheromone.x - self.x)
            angle_diff = (target_angle - self.angle) % (2 * math.pi)
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            self.angle += angle_diff * pheromone_influence  # Adjustable pheromone influence

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
            self.nest.food_deposited += 1  # Increment food deposit counter
            self.nest.total_food_collected += 1  # Increment total food collected

    def drop_pheromone(self, pheromones):
        if self.has_food and self.pheromone_timer <= 0:
            pheromones.append(Pheromone(self.x, self.y, PHEROMONE_STRENGTH, "to_nest"))
            self.pheromone_timer = PHEROMONE_DROP_INTERVAL
        else:
            self.pheromone_timer -= 1

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
        self.food_deposited = 0  # Counter for food deposits
        self.total_food_collected = 0  # Counter for total food collected
        self.total_ants_spawned = 0  # Counter for total ants spawned

    def spawn_ant(self, ants, speed):
        if self.food_deposited >= FOOD_TO_SPAWN_ANT:
            ants.append(Ant(self.x, self.y, self, speed))  # Spawn a new ant at the nest
            self.food_deposited = 0  # Reset the counter
            self.total_ants_spawned += 1  # Increment total ants spawned

    def draw(self, screen):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), NEST_SIZE)

def draw_counters(screen, ants, total_food_collected, total_ants_spawned, time_elapsed, ant_speed, pheromone_influence):
    font = pygame.font.SysFont("Consolas", 24)  # Cooler font
    y_offset = 10  # Vertical spacing between counters
    padding = 10  # Padding around the text
    max_width = 0  # Track the maximum width of the text

    # Prepare all counter texts
    counters = [
        f"Total Ants: {len(ants)}",
        f"Total Food Collected: {total_food_collected}",
        f"Ants Carrying Food: {len([ant for ant in ants if ant.has_food])}",
        f"Total Ants Spawned: {total_ants_spawned}",
        f"Time Elapsed: {time_elapsed // 60}m {time_elapsed % 60}s",
        f"Ant Speed: {ant_speed:.1f}",
        f"Pheromone Influence: {pheromone_influence:.2f}"
    ]

    # Calculate the maximum width of the texts
    for counter in counters:
        text_width, _ = font.size(counter)
        if text_width > max_width:
            max_width = text_width

    # Draw the semi-transparent background rectangle
    rect_height = len(counters) * 30 + padding * 2
    rect_width = max_width + padding * 2
    background_rect = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    background_rect.fill(COUNTER_BG_COLOR)
    screen.blit(background_rect, (10, 10))

    # Draw the border around the rectangle
    pygame.draw.rect(screen, COUNTER_BORDER_COLOR, (10, 10, rect_width, rect_height), 2)

    # Draw the counters
    for counter in counters:
        text = font.render(counter, True, WHITE)
        screen.blit(text, (10 + padding, y_offset))
        y_offset += 30

def draw_buttons(screen, font, input_text, paused, pheromone_influence):
    # Button dimensions and positions
    button_width = 150
    button_height = 40
    x_offset = WIDTH - button_width - 20
    y_offset = 20

    # Reset button
    reset_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, reset_button)
    reset_text = font.render("Reset (R)", True, BUTTON_TEXT_COLOR)
    screen.blit(reset_text, (x_offset + 10, y_offset + 10))

    # Play/Pause button
    y_offset += button_height + 10
    play_pause_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, play_pause_button)
    play_pause_text = font.render("Pause (Space)" if not paused else "Play (Space)", True, BUTTON_TEXT_COLOR)
    screen.blit(play_pause_text, (x_offset + 10, y_offset + 10))

    # Increase speed button
    y_offset += button_height + 10
    increase_speed_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, increase_speed_button)
    increase_text = font.render("Speed+ (+)", True, BUTTON_TEXT_COLOR)
    screen.blit(increase_text, (x_offset + 10, y_offset + 10))

    # Decrease speed button
    y_offset += button_height + 10
    decrease_speed_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, decrease_speed_button)
    decrease_text = font.render("Speed- (-)", True, BUTTON_TEXT_COLOR)
    screen.blit(decrease_text, (x_offset + 10, y_offset + 10))

    # Set ants button
    y_offset += button_height + 10
    set_ants_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, set_ants_button)
    set_ants_text = font.render("Set Ants", True, BUTTON_TEXT_COLOR)
    screen.blit(set_ants_text, (x_offset + 10, y_offset + 10))

    # Input box for number of ants
    y_offset += button_height + 10
    input_box = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, input_box)
    input_text_surface = font.render(input_text, True, BUTTON_TEXT_COLOR)
    screen.blit(input_text_surface, (x_offset + 10, y_offset + 10))

    # Increase pheromone influence button
    y_offset += button_height + 10
    increase_pheromone_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, increase_pheromone_button)
    increase_pheromone_text = font.render("Pheromone+", True, BUTTON_TEXT_COLOR)
    screen.blit(increase_pheromone_text, (x_offset + 10, y_offset + 10))

    # Decrease pheromone influence button
    y_offset += button_height + 10
    decrease_pheromone_button = pygame.Rect(x_offset, y_offset, button_width, button_height)
    pygame.draw.rect(screen, BUTTON_BG_COLOR, decrease_pheromone_button)
    decrease_pheromone_text = font.render("Pheromone-", True, BUTTON_TEXT_COLOR)
    screen.blit(decrease_pheromone_text, (x_offset + 10, y_offset + 10))

def reset_simulation(nest, ants, foods, pheromones, initial_ants, ant_speed):
    nest.food_deposited = 0
    nest.total_food_collected = 0
    nest.total_ants_spawned = 0
    ants.clear()
    foods.clear()
    pheromones.clear()
    ants.extend([Ant(nest.x, nest.y, nest, ant_speed) for _ in range(initial_ants)])
    foods.extend([Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(FOOD_AMOUNT)])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ant Simulation")
    clock = pygame.time.Clock()

    nest = Nest(WIDTH // 2, HEIGHT // 2)
    initial_ants = 20  # Default number of ants at start
    ant_speed = ANT_SPEED  # Default ant speed
    ants = [Ant(nest.x, nest.y, nest, ant_speed) for _ in range(initial_ants)]  # All ants start at the nest
    foods = [Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(FOOD_AMOUNT)]
    pheromones = deque()

    running = True
    paused = False  # Whether the simulation is paused
    time_elapsed = 0  # Counter for time elapsed
    input_text = ""  # Text input for number of ants
    input_active = False  # Whether the input box is active
    pheromone_influence = 0.8  # Default pheromone influence strength

    while running:
        clock.tick(FPS)
        screen.fill(GRAY)  # Changed background color to gray

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset simulation
                    reset_simulation(nest, ants, foods, pheromones, initial_ants, ant_speed)
                elif event.key == pygame.K_SPACE:  # Pause/Play simulation
                    paused = not paused
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Increase ant speed
                    ant_speed += 0.5
                    for ant in ants:
                        ant.speed = ant_speed
                elif event.key == pygame.K_MINUS:  # Decrease ant speed
                    ant_speed = max(0.5, ant_speed - 0.5)  # Prevent speed from going below 0.5
                    for ant in ants:
                        ant.speed = ant_speed
                elif event.key == pygame.K_RETURN and input_active:  # Set initial ants from input
                    try:
                        initial_ants = int(input_text)
                        reset_simulation(nest, ants, foods, pheromones, initial_ants, ant_speed)
                        input_text = ""  # Clear input box
                    except ValueError:
                        pass  # Ignore invalid input
                elif event.key == pygame.K_BACKSPACE and input_active:  # Backspace in input box
                    input_text = input_text[:-1]
                elif event.unicode.isdigit() and input_active:  # Add digit to input box
                    input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if buttons are clicked
                mouse_pos = pygame.mouse.get_pos()
                if WIDTH - 170 <= mouse_pos[0] <= WIDTH - 20:
                    if 20 <= mouse_pos[1] <= 60:  # Reset button
                        reset_simulation(nest, ants, foods, pheromones, initial_ants, ant_speed)
                    elif 80 <= mouse_pos[1] <= 120:  # Play/Pause button
                        paused = not paused
                    elif 140 <= mouse_pos[1] <= 180:  # Increase speed button
                        ant_speed += 0.5
                        for ant in ants:
                            ant.speed = ant_speed
                    elif 200 <= mouse_pos[1] <= 240:  # Decrease speed button
                        ant_speed = max(0.5, ant_speed - 0.5)
                        for ant in ants:
                            ant.speed = ant_speed
                    elif 260 <= mouse_pos[1] <= 300:  # Set ants button
                        input_active = True
                    elif 320 <= mouse_pos[1] <= 360:  # Input box
                        input_active = True
                    elif 380 <= mouse_pos[1] <= 420:  # Increase pheromone influence button
                        pheromone_influence = min(1.0, pheromone_influence + 0.1)  # Increase by 0.1
                    elif 440 <= mouse_pos[1] <= 480:  # Decrease pheromone influence button
                        pheromone_influence = max(0.0, pheromone_influence - 0.1)  # Decrease by 0.1

        if not paused:
            # Update pheromones
            for pheromone in list(pheromones):
                if not pheromone.decay():
                    pheromones.remove(pheromone)

            # Check for depleted food sources and spawn new ones
            for food in list(foods):
                if food.amount <= 0:
                    foods.remove(food)
                    foods.append(Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)))  # Spawn new food

            for ant in ants:
                ant.move()
                food = ant.sense_food(foods)
                if food and food.amount > 0:
                    ant.collect_food(food)
                if ant.has_food:
                    ant.deposit_food()
                ant.sense_pheromones(pheromones, pheromone_influence)
                ant.drop_pheromone(pheromones)

            # Spawn new ants if enough food has been deposited
            nest.spawn_ant(ants, ant_speed)

        for food in foods:
            food.draw(screen)

        for pheromone in pheromones:
            pheromone.draw(screen)

        for ant in ants:
            ant.draw(screen)

        nest.draw(screen)

        # Draw counters
        if not paused:
            time_elapsed += 1 / FPS  # Increment time elapsed
        draw_counters(screen, ants, nest.total_food_collected, nest.total_ants_spawned, int(time_elapsed), ant_speed, pheromone_influence)

        # Draw buttons
        font = pygame.font.SysFont("Consolas", 24)
        draw_buttons(screen, font, input_text, paused, pheromone_influence)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()