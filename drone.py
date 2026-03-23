from avoidance import avoid_drones, avoid_obstacles
import math

class Drone:
    def __init__(self, x, y):
        self.position = [x, y]  # position of the drone
        self.velocity = [0, 0]  # velocity with which the drone moves
        self.orientation = 0    # no change in orientation 
        self.state = "cruising" # its just moving in a straightline 
        self.radius = 50        # radius to qualify as a neighbour

    def update(self, acceleration, dt): # accelaration = (ax, ay), and dt are timesteps

        self.velocity[0] = self.velocity[0] + (acceleration[0] * dt)    # euler equation: vx = vx + ax * dt
        self.velocity[1] = self.velocity[1] + (acceleration[1] * dt)    # euler equation: vy = vy + ay * dt
        self.position[0] = self.position[0] + (self.velocity[0] * dt)   # euler equation: x = x + vx * dt
        self.position[1] = self.position[1] + (self.velocity[1] * dt)   # euler equation: y = y + vy * dt
        
    def sense(self, drones): # neighbours is a list of all drones in the world
        x = self.position[0]
        y = self.position[1]

        neighbours = []

        # calculate distance from each drone and check if within radius. if true add to the new list
        for drone in drones:
            if drone is self:
                continue

            nx = drone.position[0]
            ny = drone.position[1]
            x_distance = x - nx
            y_distance = y - ny
            euclidean_distance = math.sqrt(math.pow(x_distance, 2) + math.pow(y_distance, 2))
            if euclidean_distance <= self.radius:
                neighbours.append(drone)

        
        return neighbours
    
    def decide(self, neighbours, angles_distance): # returns the acceleration needed to update
        acceleration1 = avoid_drones(neighbours)
        acceleration2 = avoid_obstacles(self, angles_distance)

        ax = acceleration1[0] + acceleration2[0]
        ay = acceleration1[1] + acceleration2[1]
        final_acceleration = (ax, ay)

        if ax == 0 and ay == 0:
            self.state = "cruising"
        else: 
            self.state = "avoiding"

        return final_acceleration
    
    def step(self, drones, dt, angles_distance):
        neighbours= self.sense(drones)
        acceleration = self.decide(neighbours, angles_distance)
        self.update(acceleration, dt)