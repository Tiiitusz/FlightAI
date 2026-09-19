"""Box-vs-world collision: ground plane + axis-aligned boxes. Pure NumPy, no graphics.

Each contact is resolved in two parts:
    1. position: push the box out along the contact normal by the penetration depth
  2. velocity: remove the part going into the surface (with a little bounce), then apply
     Coulomb friction to the sliding part. Resting on the ground works out to friction =
     mu * g, because gravity re-adds a small inward speed every tick.
"""
import numpy as np

_UP = np.array([0.0, 1.0, 0.0])


def _respond(pos, vel, normal, penetration, restitution, friction, rest_speed):
    pos = pos + normal * penetration
    vn = float(vel @ normal)
    if vn < 0:                                              # moving into the surface
        e = restitution if -vn > rest_speed else 0.0        # slow contacts don't bounce (no jitter)
        j = -(1.0 + e) * vn                                 # normal impulse per unit mass
        vel = vel + j * normal
        vt = vel - (vel @ normal) * normal                  # sliding part
        vt_len = float(np.linalg.norm(vt))
        if vt_len > 1e-12:
            limit = friction * j                            # Coulomb: friction <= mu * normal impulse
            vel = vel - vt if vt_len <= limit else vel - vt / vt_len * limit
    return pos, vel


def _box_vs_box(pos, half_extents, bmin, bmax):
    """Return (normal, penetration) for two axis-aligned boxes, or None."""
    drone_min = pos - half_extents
    drone_max = pos + half_extents
    overlap_min = np.maximum(drone_min, bmin)
    overlap_max = np.minimum(drone_max, bmax)
    overlap = overlap_max - overlap_min

    if np.any(overlap <= 0):
        return None

    # Resolve through the shallowest face of the overlap.
    k = int(np.argmin(overlap))
    normal = np.zeros(3)
    normal[k] = -1.0 if pos[k] < (bmin[k] + bmax[k]) / 2 else 1.0
    return normal, float(overlap[k])


def resolve_box(pos, vel, half_extents, world, restitution=0.3, friction=0.6,
                   rest_speed=0.5, iterations=4):
    """Resolve a sphere against the world. Returns (new_pos, new_vel, contact_labels)."""
    pos = np.array(pos, dtype=float)
    vel = np.array(vel, dtype=float)
    labels = []

    for _ in range(iterations):                  # several passes so corners (ground + wall) settle
        touched = False

        penetration = world.ground_y + half_extents[1] - pos[1]
        if penetration > 0:
            pos, vel = _respond(pos, vel, _UP, penetration, restitution, friction, rest_speed)
            labels.append("ground")
            touched = True

        if len(world.boxes):
            drone_min = pos - half_extents
            drone_max = pos + half_extents
            near = np.nonzero(np.all((drone_min < world.maxs) & (drone_max > world.mins), axis=1))[0]
            for i in near:                                          # usually 0-2 boxes
                hit = _box_vs_box(pos, half_extents, world.mins[i], world.maxs[i])
                if hit is not None:
                    pos, vel = _respond(pos, vel, hit[0], hit[1], restitution, friction, rest_speed)
                    labels.append(f"box {i}")
                    touched = True

        if not touched:
            break

    return pos, vel, tuple(dict.fromkeys(labels))
