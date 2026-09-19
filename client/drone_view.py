from ursina import *


class DroneView(Entity):
    """The drone's 3D model (visual only). Built from primitives, X-configuration quadcopter.

    Front is +Z: the two front props are red so you can always tell which way it faces.

    Motor numbering (seen from above, front at the top):
        1 (front-left)   0 (front-right)
        2 (back-left)    3 (back-right)
    Diagonal motors spin the same way: 0 and 2 one way, 1 and 3 the other.

    `half_extents` are the sim's collision box half-widths. Press B in the client to show it.
    """

    MOTOR_OFFSET = 0.35        # motor distance from the centre along X and Z
    MAX_SPIN_DEG_S = 2500      # visual prop speed at motor input 1.0 (degrees per second)

    # (x sign, z sign, spin direction) for motors 0..3
    MOTORS = [
        (+1, +1, +1),   # 0 front-right
        (-1, +1, -1),   # 1 front-left
        (-1, -1, +1),   # 2 back-left
        (+1, -1, -1),   # 3 back-right
    ]

    def __init__(self, half_extents=(0.35, 0.3, 0.35), **kwargs):
        super().__init__(**kwargs)
        half_extents = tuple(half_extents)

        # Centre body.
        Entity(parent=self, model="cube", color=color.dark_gray, scale=(0.3, 0.08, 0.3))

        # Two crossed arms (diagonals of the X).
        arm_length = 2 * self.MOTOR_OFFSET * 2 ** 0.5
        for angle in (45, -45):
            Entity(parent=self, model="cube", color=color.gray,
                   scale=(arm_length, 0.03, 0.04), rotation_y=angle)

        # Landing legs: from the underside of the body down to the bottom of the collision box.
        leg_length = half_extents[1] - 0.04
        for sx in (-1, 1):
            for sz in (-1, 1):
                Entity(parent=self, model="cube", color=color.dark_gray,
                       scale=(0.025, leg_length, 0.025),
                       position=(sx * 0.12, -0.04 - leg_length / 2, sz * 0.12))

        # Motors + spinning props.
        self.props = []
        self.inputs = [0.0, 0.0, 0.0, 0.0]
        for sx, sz, _spin in self.MOTORS:
            pos = (sx * self.MOTOR_OFFSET, 0.0, sz * self.MOTOR_OFFSET)
            Entity(parent=self, model=Cylinder(resolution=12), color=color.black,
                   scale=(0.09, 0.07, 0.09), position=pos)
            prop = Entity(parent=self, position=(pos[0], 0.075, pos[2]))
            Entity(parent=prop, model="cube",
                   color=color.red if sz > 0 else color.light_gray,
                   scale=(0.32, 0.008, 0.035))
            self.props.append(prop)

        # Collision box, hidden until you press B.
        self.collider_view = Entity(parent=self, model="cube", scale=2 * half_extents,
                                    color=Color(0.2, 0.9, 1.0, 0.25), enabled=False)

    def toggle_collider(self):
        self.collider_view.enabled = not self.collider_view.enabled

    def set_motor_inputs(self, inputs):
        """Four values from 0 to 1. Only drives how fast the props spin (no physics)."""
        self.inputs = [clamp(v, 0, 1) for v in inputs]

    def update(self):
        # Ursina calls this every frame automatically for every Entity.
        for prop, (_, _, spin), inp in zip(self.props, self.MOTORS, self.inputs):
            prop.rotation_y += spin * inp * self.MAX_SPIN_DEG_S * time.dt
