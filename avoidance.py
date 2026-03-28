
import math

def avoid_drones(avoiding_drone, neighbours):

    avoidance_distance = 20
    x = avoiding_drone.position[0]
    y = avoiding_drone.position[1]

    ax, ay = 0, 0

    for neighbour in neighbours:
        nx = neighbour.position[0]
        ny = neighbour.position[1]
        x_distance = x - nx
        y_distance = y - ny
        euclidean_distance = math.sqrt(math.pow(x_distance, 2) + math.pow(y_distance, 2))
        
        if euclidean_distance == 0:
            continue

        if euclidean_distance <= 20:
            # since x_distance and y_distance have not been squared, hence they give us direction as well

            force_x = x_distance/euclidean_distance     # closer the drones greater the repulsive x force
            force_y = y_distance/euclidean_distance     # closer the drones greater the repulsive y force

            # we need to add the acceleration from all the neighbours to know final acceleration
            ax += force_x              
            ay += force_y

    return (ax, ay)

def avoid_obstacles(angles_distance):    

    ax, ay = 0, 0       
    force_x = 0
    force_y = 0
    for angle, distance in angles_distance:     # assuming that each at one of the eight angles is generating a distance from the farthest obstacle
        if distance is None:
            continue
        
        if distance < 50:    
            force_x += -1 * math.cos(angle)/distance    # -1 to move away, cos for the triangle forming with the angle, dividing by distance to normalize
            force_y += -1 * math.sin(angle)/distance    # explaination same as above we just have sin now because the side of the triangle has changed

    ax, ay = force_x, force_y

    return (ax, ay)