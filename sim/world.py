"""The world as plain data, shared by the physics (collision) and the client (drawing).

Coordinates: Y is up. A Box is axis-aligned, given by its centre and full size (x, y, z).
The ground is an infinite plane at y = ground_y.
"""
from dataclasses import dataclass
from random import Random

import numpy as np


@dataclass(frozen=True)
class Box:
    center: tuple
    size: tuple


class World:
    def __init__(self, boxes, ground_y=0.0):
        self.boxes = list(boxes)
        self.ground_y = ground_y
        centers = np.array([b.center for b in self.boxes], dtype=float).reshape(-1, 3)
        halves = np.array([b.size for b in self.boxes], dtype=float).reshape(-1, 3) / 2
        self.mins = centers - halves      # (N, 3) corner arrays, built once so the
        self.maxs = centers + halves      # collision code can test all boxes at once


def _overlap(a, b, margin=1.0):
    return all(abs(a.center[i] - b.center[i]) < (a.size[i] + b.size[i]) / 2 + margin for i in range(3))


def make_default_world(seed=1, num_random=40):
    """Two fixed test obstacles near the start, plus random blocks (same layout every run)."""
    fixed = [
        Box(center=(0.0, 0.5, 4.0), size=(1.5, 1.0, 1.5)),     # low pedestal: land on top of it
        Box(center=(-6.0, 1.5, 0.0), size=(0.4, 3.0, 8.0)),    # thin wall: fly into it
    ]
    boxes = list(fixed)
    rng = Random(seed)
    while len(boxes) < len(fixed) + num_random:
        x, z = rng.uniform(-40, 40), rng.uniform(-40, 40)
        height = rng.uniform(0.5, 6)
        box = Box(center=(x, height / 2, z), size=(rng.uniform(0.5, 2), height, rng.uniform(0.5, 2)))
        if abs(x) < 6 and abs(z) < 6:          # keep the start area clear
            continue
        if any(_overlap(box, f) for f in fixed):
            continue
        boxes.append(box)
    return World(boxes)
