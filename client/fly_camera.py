from ursina import *


class FlyCamera(Entity):
    """Free-fly camera: mouse look, WASD move, Space up, C down, Shift = fast, Esc = free/lock mouse."""

    def __init__(self, speed=8, sprint_multiplier=3, mouse_sensitivity=40, **kwargs):
        super().__init__(**kwargs)
        self.speed = speed
        self.sprint_multiplier = sprint_multiplier
        self.mouse_sensitivity = mouse_sensitivity

        camera.parent = self
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90

        mouse.locked = True

    def update(self):
        # Look: yaw around the world up axis, pitch clamped so you can't flip over.
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity
            self.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            self.rotation_x = clamp(self.rotation_x, -89, 89)

        # Move: forward/right follow where the camera looks (true free-fly).
        move = (
            self.forward * (held_keys["w"] - held_keys["s"])
            + self.right * (held_keys["d"] - held_keys["a"])
            + Vec3(0, 1, 0) * (held_keys["space"] - held_keys["c"])
        )
        if move.length() > 0:
            move = move.normalized()

        speed = self.speed
        if held_keys["left shift"] or held_keys["shift"]:
            speed *= self.sprint_multiplier

        self.position += move * speed * time.dt

    def input(self, key):
        if key == "escape":
            mouse.locked = not mouse.locked
