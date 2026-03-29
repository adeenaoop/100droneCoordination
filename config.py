# config.py
# All simulation constants for the 100-Drone Coordination Simulation
# Author: Eesha Ali — Milestone 1

# ─────────────────────────────────────────────
# WINDOW & DISPLAY
# ─────────────────────────────────────────────
WINDOW_TITLE   = "100 Drone Coordination Simulation"
WINDOW_WIDTH   = 1200          # pixels
WINDOW_HEIGHT  = 800           # pixels
FPS            = 30            # frames per second

# ─────────────────────────────────────────────
# SIMULATION
# ─────────────────────────────────────────────
NUM_DRONES     = 100           # total agents
DT             = 0.1           # time-step (seconds per tick)
RANDOM_SEED    = 42            # for reproducible runs
MAX_TICKS      = 3000          # stop simulation after this many ticks (0 = infinite)

# ─────────────────────────────────────────────
# WORLD / ENVIRONMENT
# ─────────────────────────────────────────────
WORLD_WIDTH    = WINDOW_WIDTH   # world units == pixels (1:1 mapping)
WORLD_HEIGHT   = WINDOW_HEIGHT
BOUNDARY_MARGIN = 130           # soft-wall repulsion starts this far from edge
BOUNDARY_FORCE  = 160          # strength of boundary push-back

# ─────────────────────────────────────────────
# SPATIAL GRID
# ─────────────────────────────────────────────
CELL_SIZE      = 80            # grid cell size in world units
                               # should be >= INTERACTION_RADIUS

# ─────────────────────────────────────────────
# DRONE PHYSICS
# ─────────────────────────────────────────────
MAX_SPEED      = 120.0         # world units per second
MAX_FORCE      = 60.0          # maximum acceleration magnitude
DRONE_RADIUS   = 8             # collision / drawing radius (pixels)
INTERACTION_RADIUS = 80        # sensing / communication range (world units)

# ─────────────────────────────────────────────
# RAY CASTING (obstacle detection)
# ─────────────────────────────────────────────
NUM_RAYS       = 8             # rays cast per drone per tick
RAY_LENGTH     = 100           # maximum ray length (world units)

# ─────────────────────────────────────────────
# COLLISION AVOIDANCE
# ─────────────────────────────────────────────
AVOIDANCE_RADIUS = 20          # personal-space radius triggering avoidance
AVOIDANCE_FORCE  = 52        # repulsion strength between drones

# ─────────────────────────────────────────────
# OBSTACLES  (list of (x, y, radius) circles)
# ─────────────────────────────────────────────
OBSTACLES = [
    (300, 200, 40),
    (600, 400, 55),
    (900, 250, 35),
    (200, 600, 45),
    (750, 600, 50),
    (1050, 500, 38),
]

# ─────────────────────────────────────────────
# DRONE STATES  (must match Hadeeqa's drone.py exactly)
# ─────────────────────────────────────────────
STATE_CRUISING  = "cruising"   # moving in a straight line (Hadeeqa's default)
STATE_AVOIDING  = "avoiding"   # actively avoiding a drone or obstacle
# Milestone 2+ states (added here so renderer is ready)
STATE_AT_TASK   = "at_task"
STATE_IDLE      = "idle"

# ─────────────────────────────────────────────
# COLOURS  (R, G, B)
# ─────────────────────────────────────────────
COLOR_BG             = (15,  15,  30)   # dark navy background
COLOR_GRID           = (30,  30,  55)   # faint grid lines
COLOR_OBSTACLE       = (180, 60,  60)   # red obstacles
COLOR_OBSTACLE_EDGE  = (220, 100, 100)
COLOR_BOUNDARY       = (60,  60,  100)  # boundary wall tint
COLOR_RAY            = (50,  200, 50,  80)  # semi-transparent green rays
COLOR_INTERACTION    = (80,  80,  200, 40)  # interaction radius ring

# Drone state colours — keyed by the exact strings Hadeeqa's drone.py sets
COLOR_DRONE = {
    STATE_CRUISING: (80,  255, 160),   # green  — normal flight
    STATE_AVOIDING: (255, 200, 50),    # yellow — active avoidance
    STATE_AT_TASK:  (255, 100, 255),   # magenta — milestone 2+
    STATE_IDLE:     (100, 180, 255),   # blue   — fallback
}
COLOR_DRONE_DEFAULT = (100, 180, 255)  # shown for any unknown state string
COLOR_DRONE_OUTLINE = (255, 255, 255)

# HUD / UI
COLOR_HUD_BG    = (0, 0, 0, 160)       # semi-transparent black panel
COLOR_HUD_TEXT  = (220, 220, 220)
COLOR_HUD_TITLE = (100, 200, 255)
COLOR_ALERT     = (255, 80,  80)

# ─────────────────────────────────────────────
# METRICS / LOGGING
# ─────────────────────────────────────────────
METRICS_CSV_PATH    = "metrics_m1.csv"
LOG_INTERVAL_TICKS  = 10   # write a CSV row every N ticks
