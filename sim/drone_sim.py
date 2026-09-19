"""The drone simulation itself. Pure Python/NumPy: no graphics, no threads, no clocks.

`step(dt)` advances the simulation by exactly `dt` seconds of *simulated* time.
It never looks at the real clock, so it behaves identically whether it is driven by a
real-time thread (the client), or called in a tight loop (RL training, tests).
"""
from dataclasses import dataclass

import numpy as np

from sim.collision import resolve_box
from sim.world import World


@dataclass(frozen=True)
class Snapshot:
    """An immutable copy of the sim state, safe to hand to another thread."""
    sim_time: float
    tick: int
    motor_inputs: tuple
    position: tuple
    velocity: tuple
    contacts: tuple      # what the drone touched during the last step, e.g. ("ground", "box 3")


class DroneSim:
    DT = 1 / 240             # fixed physics timestep in seconds
    HALF_EXTENTS = np.array([0.5, 0.1, 0.5])  # half-width, half-height, half-depth in metres
    GRAVITY = 9.81
    RESTITUTION = 0.3        # bounciness of crashes
    FRICTION = 0.6           # sliding friction against ground and boxes
    MAX_SUBSTEPS = 64
    START_POSITION = (0.0, 3.0, 0.0)

    def __init__(self, world=None):
        self.world = world if world is not None else World([])
        self.motor_inputs = np.zeros(4)            # 0..1 per motor
        self.reset()

    def reset(self, position=START_POSITION, velocity=(0.0, 0.0, 0.0)):
        self.time = 0.0
        self.tick = 0
        self.position = np.array(position, dtype=float)   # Y is up
        self.velocity = np.array(velocity, dtype=float)
        self.contacts = ()

    def set_motor_inputs(self, inputs):
        self.motor_inputs = np.clip(np.asarray(inputs, dtype=float), 0.0, 1.0)

    def step(self, dt=DT):
        # Never move more than half the smallest box extent per substep, so a fast drone can't tunnel
        # through a thin wall between two collision checks.
        speed = float(np.linalg.norm(self.velocity))
        smallest_extent = float(np.min(self.HALF_EXTENTS))
        n = min(self.MAX_SUBSTEPS, max(1, int(np.ceil(speed * dt / (0.5 * smallest_extent)))))
        sub_dt = dt / n

        hits = []
        for _ in range(n):
            # PLACEHOLDER MOTION (gravity only). Step 5 replaces this with thrust from the
            # motors, torques, rotation, drag. The collision call below stays as it is.
            self.velocity = self.velocity + np.array([0.0, -self.GRAVITY, 0.0]) * sub_dt
            self.position = self.position + self.velocity * sub_dt

            self.position, self.velocity, contacts = resolve_box(
                self.position, self.velocity, self.HALF_EXTENTS, self.world,
                restitution=self.RESTITUTION, friction=self.FRICTION,
            )
            hits.extend(contacts)

        self.contacts = tuple(dict.fromkeys(hits))
        self.time += dt
        self.tick += 1

    def snapshot(self):
        return Snapshot(
            sim_time=self.time,
            tick=self.tick,
            motor_inputs=tuple(self.motor_inputs),
            position=tuple(self.position),
            velocity=tuple(self.velocity),
            contacts=self.contacts,
        )
