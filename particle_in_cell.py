import numpy as np
from numpy.typing import NDArray
import logging
import functools
import sys
from vispy import scene, app

class Logger(logging.Logger):
    def __init__(self, name: str, level: logging.__annotations__ = logging.NOTSET):
        super().__init__(name, level)
        logging.addLevelName(15, 'PROGRESS')
        logging.addLevelName(55, 'HURRAY')

    def sep(self):
        self.info("........................................................")
    
    def log_call(self, func):
        @functools.wraps(func)
        def inner_wrapper(self_of_func, *args, **kwargs):
            self.debug(f"{func.__name__} in {self_of_func.__class__.__name__} called!")
            return func(self_of_func, *args, **kwargs)
        return inner_wrapper

logger = Logger("global_logger")
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
else:
    logger.setLevel(logging.WARNING)  # Suppress output


class Box:
    def __init__(self, length: float, periodic: bool):
        self.length = length
        self.periodic = periodic

class Simulator:
    def __init__(self, box: Box, **kwargs):
        self.box = box
        self.kwargs = kwargs
        self.required_keys = ["n_particles", "min_radius", "max_radius", "n_steps", "dt", "min_velocity", "max_velocity"]

        if set(kwargs.keys()) != set(self.required_keys):
            raise KeyError(f"Provided simulation parameters do not match the requred simulation parameters! Missing {set(self.required_keys) - set(kwargs.keys())}")

        self.n_particles = kwargs["n_particles"]
        self.min_radius = kwargs["min_radius"]
        self.max_radius = kwargs["max_radius"]
        self.n_steps = kwargs["n_steps"]
        self.dt = kwargs["dt"]
        self.min_velocity = kwargs["min_velocity"]
        self.max_velocity = kwargs["max_velocity"]
        
        self.step = 0

    def separate_particle_pair(self, distance, collective_radius, i, j):
        normal = np.nan_to_num((self.pos[i, :] - self.pos[j, :])/distance)
        # calculate the overlap distance between the two particles
        overlap = collective_radius - distance
        # shift each particle half of the overlap distance in opposite directions
        self.pos[i, :] += normal*overlap/2
        self.pos[j, :] -= normal*overlap/2
        distance = np.linalg.norm(self.pos[i, :] - self.pos[j, :])
        self.vel[i, :] -= np.nan_to_num(np.dot((self.vel[i, :] - self.vel[j, :]), (self.pos[i, :] - self.pos[j, :]))/distance**2) *  (self.pos[i, :] - self.pos[j, :])

    def track_collisions(self):
        for i in range(self.n_particles):
            for j in range(self.n_particles):
                distance = np.linalg.norm(self.pos[i, :] - self.pos[j, :])
                collective_radius = self.radii[i] + self.radii[j]

                if distance <= collective_radius:
                    self.separate_particle_pair(distance, collective_radius, i, j)

    def periodic_fwd_step(self):
        self.pos = (self.pos + self.vel*self.dt)%self.box.length
        
    def visual_periodic_fwd_step(self, event):
        if self.step > self.n_steps:
            self.timer.stop()
        self.pos = (self.pos + self.vel*self.dt)%self.box.length
        self.scatter.set_data(self.pos)
        self.step += 1
        logger.info(f"Step: {self.step} / {self.n_steps-1}")
    
    def visual_periodic_collision_fwd_step(self, event):
        if self.step > self.n_steps:
            self.timer.stop()
        self.track_collisions()
        self.pos = (self.pos + self.vel*self.dt)%self.box.length
        self.scatter.set_data(self.pos)
        self.step += 1
        logger.info(f"Step: {self.step} / {self.n_steps-1}")

    def reflective_fwd_step(self):
        self.wall_counter = 0
        for i in range(len(self.pos[:, 0])):
            if self.pos[i, 0] <= 0:
                self.vel[i, 0] = -self.vel[i, 0]
            elif self.pos[i, 0] >= self.box.length:
                self.vel[i, 0] = -self.vel[i, 0]
            elif self.pos[i, 1] <= 0:
                self.vel[i, 1] = -self.vel[i, 1]
            elif self.pos[i, 1] >= self.box.length:
                self.vel[i, 1] = -self.vel[i, 1]
            elif self.pos[i, 2] <= 0:
                self.vel[i, 2] = -self.vel[i, 2]
            elif self.pos[i, 2] >= self.box.length:
                self.vel[i, 2] = -self.vel[i, 2]

        self.pos = self.pos + self.vel*self.dt

    
    def visual_reflective_fwd_step(self, event):
        if self.step > self.n_steps:
            self.timer.stop()

        self.wall_counter = 0
        for i in range(len(self.pos[:, 0])):
            if self.pos[i, 0] <= 0:
                self.vel[i, 0] = -self.vel[i, 0]
            elif self.pos[i, 0] >= self.box.length:
                self.vel[i, 0] = -self.vel[i, 0]
            elif self.pos[i, 1] <= 0:
                self.vel[i, 1] = -self.vel[i, 1]
            elif self.pos[i, 1] >= self.box.length:
                self.vel[i, 1] = -self.vel[i, 1]
            elif self.pos[i, 2] <= 0:
                self.vel[i, 2] = -self.vel[i, 2]
            elif self.pos[i, 2] >= self.box.length:
                self.vel[i, 2] = -self.vel[i, 2]
        self.pos = self.pos + self.vel*self.dt
        self.scatter.set_data(self.pos)
        self.step += 1
        logger.info(f"Step: {self.step} / {self.n_steps-1}")

    
    def visual_reflective_collision_fwd_step(self, event):
        if self.step > self.n_steps:
            self.timer.stop()
        self.wall_counter = 0
        self.track_collisions()
        for i in range(len(self.pos[:, 0])):
            if self.pos[i, 0] <= 0:
                self.vel[i, 0] = -self.vel[i, 0]
            elif self.pos[i, 0] >= self.box.length:
                self.vel[i, 0] = -self.vel[i, 0]
            elif self.pos[i, 1] <= 0:
                self.vel[i, 1] = -self.vel[i, 1]
            elif self.pos[i, 1] >= self.box.length:
                self.vel[i, 1] = -self.vel[i, 1]
            elif self.pos[i, 2] <= 0:
                self.vel[i, 2] = -self.vel[i, 2]
            elif self.pos[i, 2] >= self.box.length:
                self.vel[i, 2] = -self.vel[i, 2]
        self.pos = self.pos + self.vel*self.dt
        self.scatter.set_data(self.pos)
        self.step += 1
        logger.info(self.wall_counter)
        #logger.info(f"Step: {self.step} / {self.n_steps-1}")

    def periodic_run(self):
        for step in range(self.n_steps):
            logger.info(f"Step: {step} / {self.n_steps-1}")
            self.periodic_fwd_step()
    
    def periodic_collision_run(self):
        self.track_collisions()
        for step in range(self.n_steps):
            logger.info(f"Step: {step} / {self.n_steps-1}")
            self.periodic_fwd_step()

        
    def reflective_run(self):
        for step in range(self.n_steps):
            logger.info(f"Step: {step} / {self.n_steps-1}")
            self.reflective_fwd_step()
    
    def reflective_collision_run(self):
        self.track_collisions()
        for step in range(self.n_steps):
            logger.info(f"Step: {step} / {self.n_steps-1}")
            self.reflective_fwd_step()
    
    def set_up_visual(self):
        self.canvas = scene.SceneCanvas(bgcolor="black", size=(300, 800), show=False)
        view = self.canvas.central_widget.add_view()
        view.camera = scene.cameras.TurntableCamera(distance=100)
        view.camera.center = (self.box.length/2, self.box.length/2, self.box.length/2)  # <-- this moves the camera center to match your box
        self.scatter = scene.visuals.Markers()
        self.scatter.set_data(self.pos, size=3, face_color="white")
        view.add(self.scatter)
        box = scene.visuals.Box(width=self.box.length, height=self.box.length, depth=self.box.length, color=(0.4, 0.7, 1, 0.15), edge_color='cyan')
        box.transform = scene.transforms.STTransform(translate=(self.box.length/2, self.box.length/2, self.box.length/2))
        view.add(box)
    
    def run(self) -> None:
        logger.sep()
        logger.info("Starting simulation run with the following parameters:")
        for key, val in zip(self.kwargs.keys(), self.kwargs.values()):
            logger.info(f"{key}:\t {val}")
        logger.info(f"Periodic box:\t {self.box.periodic}")

        self.radii: NDArray = np.random.uniform(size=(self.n_particles, 1), low=self.min_radius, high=self.max_radius)
        
        logger.sep()
        logger.info("Choosing positions and velocities...")
        self.pos: NDArray = np.random.uniform(size=(self.n_particles, 3), low=1, high=self.box.length-1)
        self.vel: NDArray = np.random.uniform(size=(self.n_particles, 3), low=self.min_velocity, high=self.max_velocity)

        logger.sep()
        logger.info("Entering dynamics ...")
            

        # here we specify the simulation mode

        if self.box.periodic and self.min_radius == 0 and self.max_radius == 0:
            self.periodic_run()
        elif self.box.periodic:
            self.periodic_collision_run()
        elif not self.box.periodic and self.min_radius == 0 and self.max_radius == 0:
            self.reflective_run()
        else:
            self.reflective_collision_run()
        
        return None


    def visual_run(self) -> None:
        logger.sep()
        logger.info("Starting simulation run with the following parameters:")
        for key, val in zip(self.kwargs.keys(), self.kwargs.values()):
            logger.info(f"{key}:\t {val}")
        logger.info(f"Periodic box:\t {self.box.periodic}")

        self.radii: NDArray = np.random.uniform(size=(self.n_particles, 1), low=self.min_radius, high=self.max_radius)
        
        logger.sep()
        logger.info("Choosing positions and velocities...")
        self.pos: NDArray = np.random.uniform(size=(self.n_particles, 3), low=1, high=self.box.length-1)
        self.vel: NDArray = np.random.uniform(size=(self.n_particles, 3), low=self.min_velocity, high=self.max_velocity)

        logger.sep()
        logger.info("Entering dynamics ...")
        
        self.set_up_visual()

        # here we specify the simulation mode

        if self.box.periodic and self.min_radius == 0 and self.max_radius == 0:
            self.timer = app.Timer(interval=1/60, connect=self.visual_periodic_fwd_step, start=True)
        elif self.box.periodic:
            self.timer = app.Timer(interval=1/60, connect=self.visual_periodic_collision_fwd_step, start=True)
        elif not self.box.periodic and self.min_radius == 0 and self.max_radius == 0:
            self.timer = app.Timer(interval=1/60, connect=self.visual_reflective_fwd_step, start=True)
        else:
            self.timer = app.Timer(interval=1/60, connect=self.visual_reflective_collision_fwd_step, start=True)

        self.canvas.show()
        app.run()
        
        return None

if __name__ == "__main__":
    box = Box(50, periodic=False)
    sim = Simulator(box, n_particles=100, min_radius=0, max_radius=0, n_steps=10000, dt=0.0001, min_velocity=0, max_velocity=500)
    sim.visual_run()

