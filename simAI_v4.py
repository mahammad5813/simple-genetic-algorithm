import pygame
import random
from dataclasses import dataclass, field
import time
import math


WIDTH, HEIGHT = 600, 600

#sim variables###############################
particle_radius = 1
particle_max_acc = 1 #maximum acceleration
air_friction = 0.06 #slows down the particle every frame

tick_speed = 60

mut_rate = 0.02 #the chance of mutating the child sample
number_of_particles = 1000
move_freq = 1
num_gens = 5000
starting_pos = [WIDTH/2, HEIGHT-50]

# grid = True
grid = False
grid_spacing = 23.06

#############color constants############
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)
#############################
particle_color = BLUE
obstacle_color = '#f76806'
target_color = RED
text_color = BLACK
bg_color = 'grey'
grid_color = (100,100,100)
color_dead = BLACK
color_reached = GREEN
#########################################
@dataclass
class Particle:
    x_pos: int
    y_pos: int
    x_vel: float = 0
    y_vel: float = 0
    fitness: float = 0
    step: int = 0
    color: tuple = particle_color
    instructions: list = field(default_factory=list)
    is_dead: bool = False
    reached_goal: bool = False
    def move_random(self):
        tot_mov = particle_max_acc
        tot_mov_x = random.uniform(0,1)
        rand_del_x = random.choice([abs(tot_mov)*tot_mov_x, -abs(tot_mov)*tot_mov_x])
        rand_del_y = random.choice([abs(tot_mov)*(1-tot_mov_x), -abs(tot_mov)*(1-tot_mov_x)])
        self.x_vel += rand_del_x
        self.y_vel += rand_del_y

        return [rand_del_x, rand_del_y]

    def move(self, instruction_step):
            self.x_vel += self.instructions[int(instruction_step)][0]
            self.y_vel += self.instructions[int(instruction_step)][1]

    def draw(self, win):
        random_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        # self.color = random_color
        pygame.draw.circle(win, self.color, (self.x_pos, self.y_pos), particle_radius)

@dataclass
class Target:
    x_pos: int
    y_pos: int
    radius: float
    color: tuple = target_color

    def draw(self, win):
        pygame.draw.circle(win,self.color,(self.x_pos, self.y_pos), self.radius)


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]


@dataclass 
class Obstacle:
    x: int
    y: int
    width: float
    height: float
    color: tuple = obstacle_color

    def draw(self, win):
        pygame.draw.rect(win,self.color,pygame.Rect(self.x, self.y, self.width, self.height))


        
def all_dead(pop):
    for particle in pop:
        if not particle.is_dead and not particle.reached_goal:
            return False
    
    return True

def sel_parent(fitness_sum, pop):
    rand = random.uniform(0, fitness_sum)
    running_sum = 0
    for particle in pop:
        running_sum += particle.fitness
        if running_sum > rand:
            return particle
    print(pop.index(particle))
    print(running_sum-rand)

def num_reached(pop):
    num = 0
    for particle in pop:
        if particle.reached_goal:
            num+=1
    return num

def main():
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    population = []
    target = Target(WIDTH/2, 50, 2)
    obstacles = [Obstacle(0, HEIGHT/2, WIDTH - 100, 10)]
    # obstacles = []
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font(),15)
    fitness_sum = 0
    refresh = True
    step_limit = 0

    for _ in range(number_of_particles):
        population.append(Particle(starting_pos[0],starting_pos[1],0,0,instructions=[]))

    for gen in range(num_gens):
        
        tick = 0
        run = True
        
        WIN.fill(bg_color)
        while run:
            if all_dead(population) or num_reached(population) >=10:
                run = False        

            if gen!=0 and tick/move_freq > step_limit >0:
                run= False

            events = pygame.event.get()
            clock.tick(tick_speed)

            if refresh:
                WIN.fill(bg_color)

            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_p:
                            run = False
                        case pygame.K_u:
                            if refresh:
                                refresh = False
                            else:
                                refresh = True
            

            for particle in population:

                particle.x_vel -= particle.x_vel*air_friction
                particle.y_vel -= particle.y_vel*air_friction

                particle.x_pos += particle.x_vel
                particle.y_pos += particle.y_vel


                dx = target.x_pos - particle.x_pos
                dy = target.y_pos - particle.y_pos
                dist = math.sqrt(dx**2+dy**2)
                
                
                if tick%move_freq ==0 and not particle.reached_goal and not particle.is_dead:
                    if gen == 0 or len(particle.instructions)<=tick/move_freq:
                        particle.instructions.append(particle.move_random())
                    else:
                        particle.move(tick/move_freq)
                    
                    particle.step += 1
                
                if dist <= particle_radius+target.radius and not particle.reached_goal:
                    particle.fitness = 10000/(particle.step**2)
                    particle.reached_goal = True
                    particle.color = color_reached
                    particle.x_vel, particle.y_vel = 0, 0
                elif not particle.reached_goal and not particle.is_dead:
                    fitness = 1/(dist**4)
                    if fitness > particle.fitness:
                        particle.fitness = fitness
                

                if not particle_radius<=particle.x_pos<=WIDTH-particle_radius:
                    particle.is_dead = True
                    particle.x_vel, particle.y_vel = 0,0
                    particle.color = color_dead

                elif not 0+particle_radius<=particle.y_pos<=HEIGHT-particle_radius:
                    particle.is_dead = True
                    particle.x_vel, particle.y_vel = 0,0
                    particle.color = color_dead

                for obstacle in obstacles:
                    if obstacle.x-particle_radius<=particle.x_pos<=obstacle.x+particle_radius + obstacle.width and obstacle.y-particle_radius<=particle.y_pos<=obstacle.y+particle_radius+obstacle.height:
                        particle.is_dead = True
                        particle.x_vel, particle.y_vel = 0, 0
                        particle.color = color_dead
                    
            if grid:
                for x in range(int(WIDTH/grid_spacing)+1):
                    pygame.draw.line(WIN, grid_color, (x*grid_spacing,0), (x*grid_spacing, HEIGHT))
                for x in range(int(HEIGHT/grid_spacing)+1):
                    pygame.draw.line(WIN, grid_color, (0,(x*grid_spacing)), (WIDTH,(x*grid_spacing)))


            for obstacle in obstacles:
                obstacle.draw(WIN)

            for particle in population:
                particle.draw(WIN)

            
            
            target.draw(WIN)
            
            
            
            # if track:
            #     text_surf = font.render(f'Number one: {number_one} Tracking: Particle {population.index(track_particle)}',True, WHITE)
            # else:
            #     text_surf = font.render(f'Number one: {number_one}',True, WHITE)
            text_surf = font.render(f'Gen {gen} Step limit: {step_limit}',True, text_color)

            WIN.blit(text_surf, (0,0))
            

            tick+=1
            pygame.display.update()

        for x in population:
            fitness_sum += x.fitness
        
        parents = []
        best_particle = None
        population.sort(key=lambda x: x.fitness)
        if population[-1].reached_goal:
            step_limit = population[-1].step
            print(f'step limit: {step_limit}')
            best_particle = population[-1]

        for _ in range(number_of_particles-1):
            parents.append(sel_parent(fitness_sum, population))

        population = []

        for particle in parents:
            instructs = []
            for instruct in particle.instructions:
                if random.uniform(0,1) < mut_rate:
                    acc = particle_max_acc
                    rat = random.uniform(0,1)
                    x_acc = random.choice([-math.sqrt((acc**2)*rat), math.sqrt((acc**2)*rat)])
                    y_acc = random.choice([-math.sqrt((acc**2)*(1-rat)), math.sqrt((acc**2)*(1-rat))])

                    instructs.append([x_acc, y_acc])
                else:
                    instructs.append(instruct)

            population.append(Particle(starting_pos[0], starting_pos[1], 0 ,0, instructions=instructs))
        
            
        if best_particle:
            population.append(Particle(starting_pos[0],starting_pos[1],0,0,instructions=best_particle.instructions))
        
        fitness_sum = 0

        

    pygame.quit()

if __name__ == '__main__':
    main()