from ursina import *

from client.world import build_world
from client.fly_camera import FlyCamera

app = Ursina(title="Drone Sim", borderless=False, vsync=True)

build_world()
cam = FlyCamera(position=(0, 2, -10))

Text(
    text="WASD move | Space up / C down | Shift fast | Mouse look | Esc free/lock mouse",
    origin=(-0.5, 0.5),
    position=window.top_left,
    scale=0.9,
)
readout = Text(origin=(-0.5, 0.5), position=window.top_left + Vec2(0, -0.04), scale=0.9)


def update():
    p = cam.position
    readout.text = f"x {p.x:6.1f}  y {p.y:6.1f}  z {p.z:6.1f}"


app.run()
