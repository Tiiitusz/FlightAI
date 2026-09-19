"""Drone sim client - window, 3D world, free-fly camera, drone model, separate physics thread.

Run from the project folder:  python main.py
"""
import atexit
import time as pytime          # Python's clock. (`time` below is Ursina's, which has time.dt)

from ursina import *

from client.world import build_world
from client.fly_camera import FlyCamera
from client.drone_view import DroneView
from sim import DroneSim, PhysicsThread, make_default_world

# ---------------------------------------------------------------------------
# WORLD + PHYSICS. The world is plain data (sim/world.py) shared by both sides: the physics
# collides against it, the client draws it. The physics runs on its own thread at a fixed
# 240 Hz, completely independent of frame rate.
# ---------------------------------------------------------------------------
world = make_default_world()
physics = PhysicsThread(DroneSim(world), rate_hz=240)
physics.set_motor_inputs([0.2, 0.4, 0.6, 0.8])      # temporary demo values (props only, no thrust yet)
atexit.register(physics.stop)

# ---------------------------------------------------------------------------
# CLIENT: window, world, camera, drone model
# ---------------------------------------------------------------------------
app = Ursina(title="Drone Sim", borderless=False, vsync=True)

build_world(world)
cam = FlyCamera(position=(0, 2, -4))
drone = DroneView(half_extents=DroneSim.HALF_EXTENTS)

Text(
    text="WASD move | Space up / C down | Shift fast | Mouse look | Esc free/lock mouse",
    origin=(-0.5, 0.5), position=window.top_left, scale=0.9,
)
Text(
    text="R drop drone | T throw drone where you look | B show collider | L lag test",
    origin=(-0.5, 0.5), position=window.top_left + Vec2(0, -0.04), scale=0.9,
)
readout = Text(origin=(-0.5, 0.5), position=window.top_left + Vec2(0, -0.08), scale=0.9)
status = Text(origin=(-0.5, 0.5), position=window.top_left + Vec2(0, -0.12), scale=0.9)
contact_text = Text(origin=(-0.5, 0.5), position=window.top_left + Vec2(0, -0.16), scale=0.9)

lag_test = False


def input(key):
    global lag_test
    if key == "l":
        lag_test = not lag_test      # slows rendering to ~10 fps; physics Hz must not change
    elif key == "r":
        physics.reset()              # back to the start point, at rest: it falls
    elif key == "t":
        f = cam.forward              # throw it from just in front of the camera, along your view
        p = cam.position + f * 1.5
        v = f * 8
        physics.reset((p.x, p.y, p.z), (v.x, v.y, v.z))
    elif key == "b":
        drone.toggle_collider()


# ---------------------------------------------------------------------------
# UPDATE CYCLE (render side only). Ursina calls update() once per frame, then each Entity's
# update(). Nothing here steps the physics: it only READS the latest snapshot and draws it.
# ---------------------------------------------------------------------------
def update():
    if lag_test:
        pytime.sleep(0.1)

    snap = physics.snapshot()
    drone.position = snap.position                 # sim state -> model (orientation comes in step 5)
    drone.set_motor_inputs(snap.motor_inputs)      # props spin speed (cosmetic)

    p = cam.position
    vx, vy, vz = snap.velocity
    readout.text = f"cam x {p.x:6.1f}  y {p.y:6.1f}  z {p.z:6.1f}"
    status.text = (f"physics {physics.measured_hz:6.1f} Hz | render {1 / time.dt:6.1f} fps | "
                   f"sim time {snap.sim_time:7.2f} s")
    contact_text.text = (f"drone y {snap.position[1]:5.2f} | speed {(vx*vx + vy*vy + vz*vz) ** 0.5:5.1f} m/s | "
                         f"touching: {', '.join(snap.contacts) or 'nothing'}")


physics.start()       # started last, so the drop begins when the window is ready
app.run()
