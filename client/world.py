from ursina import *


def build_world(world, ground_size=200):
    """Draw the shared World (sim.World). The sim collides against exactly these boxes.

    Ursina axes: X = right, Y = up, Z = forward.
    """
    Sky()

    # Ground: a big tiled plane at y = world.ground_y (the sim's ground is infinite).
    Entity(
        model="plane",
        position=(0, world.ground_y, 0),
        scale=(ground_size, 1, ground_size),
        texture="white_cube",
        texture_scale=(ground_size, ground_size),
        color=color.gray,
    )

    # Axes at the origin: X red, Y green, Z blue (each 3 units long).
    Entity(model="cube", color=color.red, scale=(3, 0.05, 0.05), position=(1.5, 0.03, 0))
    Entity(model="cube", color=color.green, scale=(0.05, 3, 0.05), position=(0, 1.5, 0))
    Entity(model="cube", color=color.blue, scale=(0.05, 0.05, 3), position=(0, 0.03, 1.5))

    # One visual cube per collision box.
    for i, box in enumerate(world.boxes):
        Entity(
            model="cube",
            texture="white_cube",
            color=color.hsv((i * 47) % 360, 0.6, 0.9),
            scale=box.size,
            position=box.center,
        )
