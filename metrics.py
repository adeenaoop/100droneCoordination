# metrics.py
# Collision logging and CSV export for Milestone 1
# Author: Eesha Ali

import csv
import os
import time
from config import METRICS_CSV_PATH, LOG_INTERVAL_TICKS


class MetricsLogger:
    """
    Tracks simulation statistics each tick and periodically writes them
    to a CSV file for post-simulation analysis with Matplotlib.

    Tracked metrics (Milestone 1):
        - tick               : current simulation tick
        - elapsed_time       : wall-clock seconds since simulation start
        - collisions_this_tick : drone-drone collisions detected this tick
        - total_collisions   : cumulative collision count
        - avg_speed          : mean drone speed across all agents
        - active_drones      : number of drones still in simulation
    """

    # CSV column headers — extend in later milestones
    FIELDNAMES = [
        "tick",
        "elapsed_time",
        "collisions_this_tick",
        "total_collisions",
        "avg_speed",
        "active_drones",
    ]

    def __init__(self, csv_path: str = METRICS_CSV_PATH):
        self.csv_path       = csv_path
        self.tick           = 0
        self.total_collisions = 0
        self._start_time    = time.time()
        self._rows_buffer   = []          # accumulate rows before flushing

        # Create / overwrite CSV and write header
        self._init_csv()

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def update(self, drones: list, collisions_this_tick: int) -> None:
        """
        Call once per simulation tick.

        Parameters
        ----------
        drones              : list of Drone objects (must have .velocity attribute)
        collisions_this_tick: number of collisions detected in this tick
        """
        self.tick += 1
        self.total_collisions += collisions_this_tick

        speeds = [_magnitude(d.velocity) for d in drones if hasattr(d, "velocity")]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0

        row = {
            "tick":                 self.tick,
            "elapsed_time":         round(time.time() - self._start_time, 3),
            "collisions_this_tick": collisions_this_tick,
            "total_collisions":     self.total_collisions,
            "avg_speed":            round(avg_speed, 3),
            "active_drones":        len(drones),
        }

        self._rows_buffer.append(row)

        # Flush to disk every LOG_INTERVAL_TICKS ticks
        if self.tick % LOG_INTERVAL_TICKS == 0:
            self._flush()

    def record_collision(self, count: int = 1) -> None:
        """Convenience: manually add collisions outside the update() call."""
        self.total_collisions += count

    def close(self) -> None:
        """Flush any remaining buffered rows. Call when simulation ends."""
        self._flush()
        print(f"[Metrics] Saved {self.tick} ticks → {self.csv_path}")
        print(f"[Metrics] Total collisions recorded: {self.total_collisions}")

    def get_summary(self) -> dict:
        """Return a summary dict for display on the HUD or console."""
        return {
            "tick":             self.tick,
            "total_collisions": self.total_collisions,
        }

    # ──────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────

    def _init_csv(self) -> None:
        """Create the CSV file and write the header row."""
        os.makedirs(os.path.dirname(self.csv_path) if os.path.dirname(self.csv_path) else ".", exist_ok=True)
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()

    def _flush(self) -> None:
        """Append buffered rows to the CSV file."""
        if not self._rows_buffer:
            return
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerows(self._rows_buffer)
        self._rows_buffer.clear()


# ──────────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────────

def _magnitude(vec) -> float:
    """Return the length of a 2-tuple / list vector."""
    try:
        return (vec[0] ** 2 + vec[1] ** 2) ** 0.5
    except (TypeError, IndexError):
        return 0.0


# ──────────────────────────────────────────────────────────────
# Quick self-test  (run: python metrics.py)
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import random

    class _FakeDrone:
        def __init__(self):
            self.velocity = (random.uniform(-50, 50), random.uniform(-50, 50))

    logger = MetricsLogger(csv_path="test_metrics.csv")
    drones = [_FakeDrone() for _ in range(100)]

    for _ in range(50):
        logger.update(drones, collisions_this_tick=random.randint(0, 3))

    logger.close()
    print("Self-test complete. Check test_metrics.csv")
