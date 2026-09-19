"""Runs a DroneSim on its own thread at a fixed real-time rate, independent of rendering.

The renderer never steps the physics. It only:
  - calls set_motor_inputs(...)   (client -> sim)
  - calls snapshot()              (sim -> client)
so a slow, stuttering or paused render loop cannot change how fast the physics runs.

For RL training you do NOT use this class: call DroneSim.step() directly in a loop,
as fast as the CPU allows.
"""
import threading
import time


class PhysicsThread:
    def __init__(self, sim, rate_hz=240):
        self.sim = sim
        self.dt = 1.0 / rate_hz
        self.measured_hz = 0.0      # actual steps per real second, updated once per second

        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="physics", daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

    # ---- called from the client (render) thread -------------------------------------------
    def set_motor_inputs(self, inputs):
        with self._lock:
            self.sim.set_motor_inputs(inputs)

    def reset(self, position=None, velocity=(0.0, 0.0, 0.0)):
        with self._lock:
            if position is None:
                self.sim.reset()
            else:
                self.sim.reset(position, velocity)

    def snapshot(self):
        with self._lock:
            return self.sim.snapshot()

    # ---- physics thread ---------------------------------------------------------------------
    def _run(self):
        next_time = time.perf_counter()
        window_start = next_time
        steps = 0

        while not self._stop.is_set():
            with self._lock:
                self.sim.step(self.dt)
            steps += 1

            # Absolute deadlines: sleep jitter self-corrects, so the average rate stays exact.
            next_time += self.dt
            now = time.perf_counter()
            if next_time - now > 0:
                time.sleep(next_time - now)
            elif now - next_time > 0.25:
                next_time = now     # badly behind (e.g. laptop suspended): drop the backlog

            now = time.perf_counter()
            if now - window_start >= 1.0:
                self.measured_hz = steps / (now - window_start)
                steps = 0
                window_start = now
