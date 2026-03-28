# main_demo.py  —  Milestone 1 integration
# Wires together all three members' code.
#
# ⚠ BUG NOTE FOR HADEEQA:
#   avoidance.py defines:   avoid_obstacle(...)
#   drone.py imports:       avoid_obstacles(...)   ← extra 's'
#   Fix: rename the function in avoidance.py to avoid_obstacles

import random
import math
import pygame

from config import (
    FPS, NUM_DRONES, WINDOW_WIDTH, WINDOW_HEIGHT,
    DT, RANDOM_SEED, MAX_TICKS, OBSTACLES,
    AVOIDANCE_RADIUS, BOUNDARY_MARGIN, BOUNDARY_FORCE,
    NUM_RAYS, RAY_LENGTH,
)
from renderer import Renderer
from metrics  import MetricsLogger
from drone    import Drone          # Hadeeqa's file

random.seed(RANDOM_SEED)


# ── Spawn ──────────────────────────────────────────────────

def spawn_drones(n):
    drones = []
    for i in range(n):
        x = random.uniform(BOUNDARY_MARGIN + 10, WINDOW_WIDTH  - BOUNDARY_MARGIN - 10)
        y = random.uniform(BOUNDARY_MARGIN + 10, WINDOW_HEIGHT - BOUNDARY_MARGIN - 10)
        d = Drone(ID=i, x=x, y=y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(30, 80)
        d.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        drones.append(d)
    return drones


# ── Ray casting ────────────────────────────────────────────

def cast_rays(drone):
    """Returns (angles_distances, ray_segments) for decide() and renderer."""
    px, py = drone.position
    heading = math.atan2(drone.velocity[1], drone.velocity[0]) if any(drone.velocity) else 0.0

    angles_distances, ray_segments = [], []

    for i in range(NUM_RAYS):
        angle = heading + i * (2 * math.pi / NUM_RAYS)
        dx, dy = math.cos(angle), math.sin(angle)
        hit_dist = None
        end_x = px + dx * RAY_LENGTH
        end_y = py + dy * RAY_LENGTH

        for (ox, oy, r) in OBSTACLES:
            fx, fy = px - ox, py - oy
            a = dx*dx + dy*dy
            b = 2 * (fx*dx + fy*dy)
            c = fx*fx + fy*fy - r*r
            disc = b*b - 4*a*c
            if disc >= 0:
                t = (-b - math.sqrt(disc)) / (2*a)
                if 0 < t < RAY_LENGTH and (hit_dist is None or t < hit_dist):
                    hit_dist = t
                    end_x = px + dx * t
                    end_y = py + dy * t

        angles_distances.append((angle, hit_dist))
        ray_segments.append(((px, py), (end_x, end_y)))

    return angles_distances, ray_segments


# ── Soft boundary force ────────────────────────────────────

def boundary_force(drone):
    px, py = drone.position
    ax, ay = 0.0, 0.0
    m, f = BOUNDARY_MARGIN, BOUNDARY_FORCE
    if px < m:
        ax += f * (1 - px / m)
    elif px > WINDOW_WIDTH - m:
        ax -= f * (1 - (WINDOW_WIDTH - px) / m)
    if py < m:
        ay += f * (1 - py / m)
    elif py > WINDOW_HEIGHT - m:
        ay -= f * (1 - (WINDOW_HEIGHT - py) / m)
    return ax, ay


# ── Collision count (for metrics) ──────────────────────────

def count_collisions(drones):
    count = 0
    n = len(drones)
    for i in range(n):
        for j in range(i + 1, n):
            dx = drones[i].position[0] - drones[j].position[0]
            dy = drones[i].position[1] - drones[j].position[1]
            if math.sqrt(dx*dx + dy*dy) < AVOIDANCE_RADIUS:
                count += 1
    return count


# ── Main loop ──────────────────────────────────────────────

def main():
    renderer = Renderer()
    metrics  = MetricsLogger()
    drones   = spawn_drones(NUM_DRONES)
    tick     = 0
    running  = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            renderer.handle_event(event)

        for drone in drones:
            angles_distances, ray_segs = cast_rays(drone)
            drone.rays = ray_segs                        # renderer reads this
            neighbours   = drone.sense(drones)
            acceleration = drone.decide(neighbours, angles_distances)
            bx, by = boundary_force(drone)
            drone.update((acceleration[0] + bx, acceleration[1] + by), DT)

        coll = count_collisions(drones)
        metrics.update(drones, coll)
        tick += 1

        fps = renderer.clock.get_fps()
        renderer.draw(drones, tick, fps, metrics.get_summary())
        renderer.draw_legend()
        pygame.display.flip()
        renderer.tick(FPS)

        if MAX_TICKS and tick >= MAX_TICKS:
            running = False

    metrics.close()
    renderer.quit()


if __name__ == "__main__":
    main()
