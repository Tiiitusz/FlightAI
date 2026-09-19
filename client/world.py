from random import Random

from ursina import *


def build_world(size=200, num_landmarks=40, seed=1):
    """Ground, sky, axes at the origin and some coloured blocks to judge movement against.

    Ursina axes: X = right, Y = up, Z = forward.
    """
    Sky()

    # Ground: a big plane with a tiled grid texture.
    Entity(
        model="plane",
        scale=(size, 1, size),
        texture="white_cube",
        texture_scale=(size, size),
        color=color.gray,
    )

    # Axes at the origin: X red, Y green, Z blue (each 3 units long).
    Entity(model="cube", color=color.red, scale=(3, 0.05, 0.05), position=(1.5, 0.03, 0))
    Entity(model="cube", color=color.green, scale=(0.05, 3, 0.05), position=(0, 1.5, 0))
    Entity(model="cube", color=color.blue, scale=(0.05, 0.05, 3), position=(0, 0.03, 1.5))

    # Random landmark blocks (same layout every run because of the fixed seed).
    rng = Random(seed)
    placed = 0
    while placed < num_landmarks:
        x, z = rng.uniform(-40, 40), rng.uniform(-40, 40)
        if abs(x) < 6 and abs(z) < 6:  # keep the start area clear
            continue
        height = rng.uniform(0.5, 6)
        Entity(
            model="cube",
            texture="white_cube",
            color=color.hsv(rng.uniform(0, 360), 0.6, 0.9),
            scale=(rng.uniform(0.5, 2), height, rng.uniform(0.5, 2)),
            position=(x, height / 2, z),
        )
        placed += 1
