# renderer.py
# Pygame visualisation for the 100-Drone Coordination Simulation — Milestone 1
# Author: Eesha Ali
#
# Draws:
#   • Dark background + optional faint grid
#   • Circular obstacles (filled + edge ring)
#   • Soft boundary wall tint
#   • Each drone as a filled triangle pointing in its heading direction
#     – colour-coded by state (idle / moving / avoiding / at_task)
#     – white outline
#   • Debug overlays (toggle with keys):
#       D  →  interaction-radius ring per drone
#       R  →  ray-cast lines per drone
#   • HUD panel (top-left): tick, FPS, collision count, active drones, keybindings

import math
import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    DRONE_RADIUS, INTERACTION_RADIUS, NUM_RAYS, RAY_LENGTH,
    COLOR_BG, COLOR_GRID, COLOR_OBSTACLE, COLOR_OBSTACLE_EDGE,
    COLOR_BOUNDARY, COLOR_DRONE, COLOR_DRONE_OUTLINE, COLOR_DRONE_DEFAULT,
    COLOR_HUD_BG, COLOR_HUD_TEXT, COLOR_HUD_TITLE, COLOR_ALERT,
    OBSTACLES, BOUNDARY_MARGIN,
    STATE_CRUISING, STATE_AVOIDING, STATE_AT_TASK, STATE_IDLE,
)


# ──────────────────────────────────────────────
# Module-level helpers
# ──────────────────────────────────────────────

def _heading(velocity) -> float:
    """Return angle (radians) from a velocity 2-tuple. 0 = right, +ve = CW."""
    vx, vy = velocity
    if vx == 0 and vy == 0:
        return 0.0
    return math.atan2(vy, vx)


def _triangle_points(cx: float, cy: float, angle: float, size: float):
    """
    Return 3 points for a triangle sprite centred at (cx, cy),
    pointing in direction `angle` (radians), with half-length `size`.
    """
    tip_len  = size * 1.6      # nose
    base_len = size * 0.9      # half-width of the base

    # Tip (front)
    tx = cx + tip_len  * math.cos(angle)
    ty = cy + tip_len  * math.sin(angle)

    # Two base corners (perpendicular to heading)
    perp = angle + math.pi / 2
    bx1 = cx - base_len * math.cos(angle) + base_len * math.cos(perp)
    by1 = cy - base_len * math.sin(angle) + base_len * math.sin(perp)
    bx2 = cx - base_len * math.cos(angle) - base_len * math.cos(perp)
    by2 = cy - base_len * math.sin(angle) - base_len * math.sin(perp)

    return [(tx, ty), (bx1, by1), (bx2, by2)]


# ──────────────────────────────────────────────
# Renderer class
# ──────────────────────────────────────────────

class Renderer:
    """
    Encapsulates all Pygame drawing for Milestone 1.

    Usage
    -----
    renderer = Renderer()
    ...
    while running:
        for event in pygame.event.get():
            renderer.handle_event(event)
        renderer.draw(drones, tick, fps, metrics_summary)
    renderer.quit()
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock  = pygame.time.Clock()
        self.font_sm = pygame.font.SysFont("monospace", 13)
        self.font_md = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_lg = pygame.font.SysFont("monospace", 20, bold=True)

        # Debug toggles (press D / R in simulation)
        self.show_interaction_radius = False
        self.show_rays               = False
        self.show_grid               = False

        # Surface for alpha blending
        self._overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    # ── Public ─────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        """Pass Pygame events here to handle debug key toggles."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.show_interaction_radius = not self.show_interaction_radius
            elif event.key == pygame.K_r:
                self.show_rays = not self.show_rays
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid

    def draw(self, drones: list, tick: int, fps: float, metrics: dict) -> None:
        """
        Main draw call. Call once per simulation tick.

        Parameters
        ----------
        drones  : list of Drone objects
                  Required attributes per drone:
                    .position  → (x, y)
                    .velocity  → (vx, vy)
                    .state     → one of STATE_* strings
                    .rays      → list of ((x1,y1),(x2,y2)) ray segments (optional)
        tick    : current simulation tick number
        fps     : measured frames-per-second
        metrics : dict from MetricsLogger.get_summary()
        """
        self.screen.fill(COLOR_BG)

        if self.show_grid:
            self._draw_grid()

        self._draw_boundary()
        self._draw_obstacles()

        # Per-drone debug overlays (drawn before sprites so sprites appear on top)
        if self.show_interaction_radius or self.show_rays:
            self._overlay.fill((0, 0, 0, 0))
            for drone in drones:
                if self.show_interaction_radius:
                    self._draw_interaction_ring(drone)
                if self.show_rays and hasattr(drone, "rays"):
                    self._draw_rays(drone)
            self.screen.blit(self._overlay, (0, 0))

        # Drone sprites
        for drone in drones:
            self._draw_drone(drone)

        # HUD (drawn last — on top of everything)
        self._draw_hud(tick, fps, metrics, len(drones))

        pygame.display.flip()

    def tick(self, fps_cap: int) -> float:
        """Advance clock; return actual FPS."""
        return self.clock.tick(fps_cap)

    def quit(self) -> None:
        pygame.quit()

    # ── Private drawing helpers ─────────────────

    def _draw_grid(self) -> None:
        """Faint background grid."""
        from config import CELL_SIZE
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

    def _draw_boundary(self) -> None:
        """Dim rectangle showing the soft-wall exclusion zone."""
        m = BOUNDARY_MARGIN
        rect = pygame.Rect(m, m, WINDOW_WIDTH - 2 * m, WINDOW_HEIGHT - 2 * m)
        pygame.draw.rect(self.screen, COLOR_BOUNDARY, rect, 2)

    def _draw_obstacles(self) -> None:
        """Draw all circular obstacles defined in config."""
        for (ox, oy, r) in OBSTACLES:
            pygame.draw.circle(self.screen, COLOR_OBSTACLE,       (int(ox), int(oy)), int(r))
            pygame.draw.circle(self.screen, COLOR_OBSTACLE_EDGE,  (int(ox), int(oy)), int(r), 2)

    def _draw_drone(self, drone) -> None:
        """Draw a triangular sprite for one drone, colour-coded by state."""
        px, py = drone.position
        state  = getattr(drone, "state", STATE_CRUISING)
        # Graceful fallback: if state string is unrecognised, use default colour
        color  = COLOR_DRONE.get(state, COLOR_DRONE_DEFAULT)
        angle  = _heading(drone.velocity)

        pts = _triangle_points(px, py, angle, DRONE_RADIUS)

        # Filled body
        pygame.draw.polygon(self.screen, color, pts)
        # White outline
        pygame.draw.polygon(self.screen, COLOR_DRONE_OUTLINE, pts, 1)

    def _draw_interaction_ring(self, drone) -> None:
        """Semi-transparent interaction-radius circle on the overlay surface."""
        px, py = drone.position
        pygame.draw.circle(
            self._overlay,
            (80, 80, 200, 30),          # soft blue, mostly transparent
            (int(px), int(py)),
            int(INTERACTION_RADIUS),
            1,
        )

    def _draw_rays(self, drone) -> None:
        """Draw ray-cast lines on the overlay surface."""
        for (start, end) in drone.rays:
            pygame.draw.line(
                self._overlay,
                (50, 220, 50, 90),       # semi-transparent green
                (int(start[0]), int(start[1])),
                (int(end[0]),   int(end[1])),
                1,
            )

    def _draw_hud(self, tick: int, fps: float, metrics: dict, active: int) -> None:
        """
        HUD panel in the top-left corner.
        Shows: title, tick, fps, collisions, active drones, keybindings.
        """
        panel_w, panel_h = 280, 220
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 160))
        self.screen.blit(panel_surf, (8, 8))

        lines = [
            ("HUD", self.font_lg, COLOR_HUD_TITLE),
            (None, None, None),                                       # spacer
            (f"Tick          : {tick}",          self.font_sm, COLOR_HUD_TEXT),
            (f"FPS           : {fps:.1f}",        self.font_sm, COLOR_HUD_TEXT),
            (f"Active drones : {active}",         self.font_sm, COLOR_HUD_TEXT),
            (f"Total collisions: {metrics.get('total_collisions', 0)}",
                                                  self.font_sm,
                                                  COLOR_ALERT if metrics.get('total_collisions', 0) > 0
                                                  else COLOR_HUD_TEXT),
            (None, None, None),
            ("─── Debug Overlays ───",            self.font_sm, COLOR_HUD_TITLE),
            (f"[D] Interaction ring : {'ON' if self.show_interaction_radius else 'off'}",
                                                  self.font_sm, COLOR_HUD_TEXT),
            (f"[R] Ray casts        : {'ON' if self.show_rays else 'off'}",
                                                  self.font_sm, COLOR_HUD_TEXT),
            (f"[G] Grid             : {'ON' if self.show_grid else 'off'}",
                                                  self.font_sm, COLOR_HUD_TEXT),
            (None, None, None),
            ("[ESC] Quit",                        self.font_sm, COLOR_HUD_TEXT),
        ]

        y = 14
        for (text, font, color) in lines:
            if text is None:
                y += 6
                continue
            surf = font.render(text, True, color)
            self.screen.blit(surf, (16, y))
            y += font.get_linesize() + 2

    # ── Legend ─────────────────────────────────

    def draw_legend(self) -> None:
        """
        Draws a small colour-legend in the bottom-left corner.
        Optional — call from main loop if desired.
        """
        items = [
            (STATE_CRUISING, "Cruising"),
            (STATE_AVOIDING, "Avoiding"),
            (STATE_AT_TASK,  "At task (M2+)"),
            (STATE_IDLE,     "Idle"),
        ]
        x, y0 = 10, WINDOW_HEIGHT - 110
        panel = pygame.Surface((160, 100), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        self.screen.blit(panel, (x - 4, y0 - 4))

        for i, (state, label) in enumerate(items):
            color = COLOR_DRONE[state]
            cy = y0 + i * 22
            pygame.draw.circle(self.screen, color, (x + 8, cy + 8), 6)
            txt = self.font_sm.render(label, True, COLOR_HUD_TEXT)
            self.screen.blit(txt, (x + 20, cy))
