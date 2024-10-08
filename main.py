import pygame
import os
import math
import sys

import neat

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 563

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255)

# Generation counter
currentGeneration = 0

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Car")

# The track is defined as the track labeled track.png.
# To load a new track, rename the desired track to "track.png" in the Asseets folder
TRACK = pygame.image.load("Assets/track.png")

# The Car class.  Needs to be moved to seperate file!
class Car(pygame.sprite.Sprite) :
    def __init__(self) :
        super().__init__()
        self.original_image = pygame.image.load(os.path.join("Assets", "car.png"))
        self.image = self.original_image
        self.rect = self.image.get_rect(center = (481, 520))
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []
        
    # 
    def update(self) :
        self.radars.clear()
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60) :
            self.radar(radar_angle)
        self.collision()
        self.data()
        
    def drive(self) :
        self.rect.center += self.vel_vector * 5
            
    def collision(self) :
        length = 15
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]
        
        try :
        
            if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
               or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255) :
                self.alive = False
                
        except :
            pass
            
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)
            
    def rotate(self) :
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
            
        if self.direction == -1 :
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)
            
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center = self.rect.center)
        
    def radar(self, radar_angle) :
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])
        
        try :
        
            while not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 200 :
                length += 1
                x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
                y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length) 
                
        except :
            
            pass
            
            
        pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)
        
        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                   + math.pow(self.rect.center[1] - y, 2)))
        
        self.radars.append([radar_angle, dist])
        
    def data(self) :
        input = [0, 0, 0, 0, 0]
        
        for i, radar in enumerate(self.radars) :
            input[i] = int(radar[1])
        return input
    
def remove(index) :
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)

def eval_genomes(genomes, config) :
    
    global cars, ge, nets
    
    cars = []
    ge = []
    nets = []
    
    for genomeid, genome in genomes :
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        
    # Set the game state
    run = True
    while run :
        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                pygame.quit()
                sys.exit()
                
        SCREEN.blit(TRACK, (0, 0))
        
        if len(cars) == 0 :
            break
        
        for i, car in enumerate(cars) :
            ge[i].fitness += 1
            if not car.sprite.alive :
                remove(i)
                
        # Car controls
        for i, car in enumerate(cars) :
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7 :
                car.sprite.direction = 1
            if output[1] > 0.7 :
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7 :
                car.sprite.direciton = 0
            
        for car in cars :
            car.draw(SCREEN)
            car.update()
            
        pygame.display.update()
        
def run(path_to_config) :
    global pop
    
    # NEAT Configuration
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        path_to_config
        )
    
    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    pop.run(eval_genomes, 50)
    
if __name__ == "__main__" :
    localDirectory = os.path.dirname(__file__)
    config_path = os.path.join(localDirectory, "config.txt")
    run(config_path)