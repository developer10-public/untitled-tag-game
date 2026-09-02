from builtins import *
import lmstudio
from constants import *
from concurrent.futures import ThreadPoolExecutor
from typing import TypeAlias, Optional
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import SmoothFollow
from ursina.entity import Entity
from os import path, chdir
from sys import platform
from socket import socket, AF_INET, SOCK_STREAM
HostType:TypeAlias = str
# Prototypes
class ThirdPersonController(Entity):... #COMPLETED
class Base(Entity):... #COMPLETED
class Gun(Base):... #COMPLETED
class Wall(Base):... #COMPLETED
class Ground(Base):... #COMPLETED
class Sky(Base):... #COMPLETED
class Player(Base):... #COMPLETED
class Bot(Base):... #COMPLETED
class Opponent(Base):...
class Server(socket):... #COMPLETED
class Client(socket):... #COMPLETED
class Sniper(Gun):... #COMPLETED
class AutoGun(Gun):... #COMPLETED
class AWP(Sniper):... #COMPLETED
class AK47(AutoGun):... #COMPLETED
class Animations:...
class GetMoveBots:... #COMPLETED
class AILoader:... #COMPLETED
def input(key):...
def update():...
# Define
class ThirdPersonController(Entity):
    def __init__(self, height=2, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__(enabled=False)
        self.speed = 5
        self.height = height
        self.camera_pivot = Entity(parent=self, y=self.height)

        camera.parent = self.camera_pivot
        camera.position = Vec3.zero
        camera.rotation = Vec3.zero
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35 # will interrupt jump up
        self.jumping = False
        self.air_time = 0

        self.traverse_target = scene     # by default, it will collide with everything. change this to change the raycasts' traverse targets.
        self.ignore_list = [self, ]
        self.on_destroy = self.on_disable

        for key, value in kwargs.items():
            setattr(self, key ,value)

        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)
            if ray.hit:
                self.y = ray.world_point.y


    def on_window_ready(self):
        camera.rotation = Vec3.zero


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, traverse_target=self.traverse_target, ignore=self.ignore_list, distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, traverse_target=self.traverse_target, ignore=self.ignore_list, distance=.5, debug=False)
        if not feet_ray.hit and not head_ray.hit:
            move_amount = self.direction * time.dt * self.speed

            if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[0] = min(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[0] = max(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[2] = min(move_amount[2], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[2] = max(move_amount[2], 0)
            self.position += move_amount

            # self.position += self.direction * self.speed * time.dt


        if self.gravity:
            # gravity
            ray = raycast(self.world_position+(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity


    def input(self, key):
        if key == 'space':
            self.jump()

    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True


    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True
        # restore parent and position/rotation from before disablem in case you moved the camera in the meantime.
        if hasattr(self, 'camera_pivot') and hasattr(self, '_original_camera_transform'):
            camera.parent = self.camera_pivot
            camera.transform = self._original_camera_transform


    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False
        self._original_camera_transform = camera.transform  # store original position and rotation
        camera.world_parent = scene
class Base(Entity):
    "Common base class for all entities"
    def __init__(self,
            add_to_scene_entities=True,
            enabled=True,
            parent=scene,
            position=Vec3(0,0,0),
            rotation=Vec3(0,0,0),
            scale=Vec3(1,1,1),
            model='',
            origin=Vec3(0,0,0),
            shader=Default,
            color=color.white,
            texture='',
            texture_scale=Vec2.one,
            texture_offset=Vec2.zero,
            collider=None,
            ignore_paused=Default,
            eternal=False,
            name='',
            **kwargs
            ):
        super().__init__(add_to_scene_entities, enabled, parent, position, rotation, scale, model, origin, shader, color, texture, texture_scale, texture_offset, collider, ignore_paused, eternal, name, **kwargs)
class Gun(Base):
    "Common base class for all type of guns."
    def __init__(self, model:str, scale:tuple, texture:str, texture_scale:str):
        super().__init__(model=path.abspath(model), scale=scale, texture=path.abspath(texture), texture_scale=texture_scale)
class Sniper(Gun):
    "Common base class for all snipers."
    def __init__(self, model, scale, texture, texture_scale, model_name:str):
        super().__init__(model=path.abspath(model), scale=scale, texture=path.abspath(texture), texture_scale=texture_scale)
        self.model_names = []
        self.model_names.append(model_name)
        # Scope States
        self.normal_fov = 90
        self.scoped_fov = 10
        self.is_scoped = False
        
        # Ammo & Reload Parameters
        self.max_ammo = 100
        self.current_ammo = 5
        self.reload_time = 2.5   # Time in seconds to reload
        self.fire_rate = 1.5     # Delay between bolt-action shots
        
        # Cooldown Timers
        self.is_reloading = False
        self.can_shoot = True
        
        # Scope Reticle UI
        self.scope_overlay = Entity(
            parent=camera.ui,
            model='quad',
            texture='circle', 
            color=color.black66,
            scale=(1.8, 1),
            enabled=False
        )

    def shoot(self, enemy_list):
        # Prevent firing if out of ammo, currently reloading, or on fire-rate cooldown
        if not self.can_shoot or self.is_reloading:
            return
            
        if self.current_ammo <= 0:
            print("Out of ammo! Press R to reload.")
            return

        # Deduct ammo & trigger fire-rate cooldown
        self.current_ammo -= 1
        self.can_shoot = False
        invoke(setattr, self, 'can_shoot', True, delay=self.fire_rate)
        
        print(f"AWP Fired! Ammo remaining: {self.current_ammo}/{self.max_ammo}")

        # Raycast shot logic from screen center
        hit_info = raycast(camera.world_position, camera.forward, distance=200)
        if hit_info.hit and hit_info.entity in enemy_list:
            hit_info.entity.tag()

    def reload(self):
        # Don't reload if magazine is full or already reloading
        if self.is_reloading or self.current_ammo == self.max_ammo:
            return
            
        print("Reloading AWP...")
        self.is_reloading = True
        
        # Temporarily drop scope during reload animation/delay
        if self.is_scoped:
            self.scope_overlay.enabled = False
            camera.fov = self.normal_fov

        # Refill ammo after reload duration finishes
        invoke(self._finish_reload, delay=self.reload_time)

    def _finish_reload(self):
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        print("Reload complete!")

    def toggle_scope(self, player_mesh):
        # Block scoping while reloading
        if self.is_reloading:
            return

        self.is_scoped = held_keys['right mouse']
        target_fov = self.scoped_fov if self.is_scoped else self.normal_fov
        
        camera.fov = lerp(camera.fov, target_fov, time.dt * 12)
        self.scope_overlay.enabled = self.is_scoped
        
        if player_mesh:
            player_mesh.enabled = not self.is_scoped
class AutoGun(Gun):
    "Common base class for all auto guns."
    def __init__(self, model, scale, texture, texture_scale, model_name:str):
        super().__init__(model=path.abspath(model), scale=scale, texture=path.abspath(texture), texture_scale=texture_scale)
        self.model_names = []
        self.model_names.append(model_name)
        
        # Scope States
        self.normal_fov = 90
        self.scoped_fov = 20
        self.is_scoped = False
        
        # Ammo & Reload Parameters
        self.max_ammo = 300
        self.current_ammo = 30
        self.reload_time = 2.5       # Time in seconds to reload
        self.fire_rate = 1.2         # Delay between bolt-action shots
        
        # Cooldown Timers
        self.is_reloading = False
        self.can_shoot = True
        
        # Scope Reticle UI
        self.scope_overlay = Entity(
            parent=camera.ui,
            model='quad',
            texture='circle', 
            color=color.black66,
            scale=(1.8, 1),
            enabled=False
        )

    def shoot(self, enemy_list):
        # Prevent firing if out of ammo, currently reloading, or on fire-rate cooldown
        if not self.can_shoot or self.is_reloading:
            return
            
        if self.current_ammo <= 0:
            print("Out of ammo! Press R to reload.")
            return

        # Deduct ammo & trigger fire-rate cooldown
        self.current_ammo -= 1
        self.can_shoot = False
        invoke(setattr, self, 'can_shoot', True, delay=self.fire_rate)
        
        print(f"AWP Fired! Ammo remaining: {self.current_ammo}/{self.max_ammo}")

        # Raycast shot logic from screen center
        hit_info = raycast(camera.world_position, camera.forward, distance=200)
        if hit_info.hit and hit_info.entity in enemy_list:
            hit_info.entity.tag()

    def reload(self):
        # Don't reload if magazine is full or already reloading
        if self.is_reloading or self.current_ammo == self.max_ammo:
            return
            
        print("Reloading AWP...")
        self.is_reloading = True
        
        # Temporarily drop scope during reload animation/delay
        if self.is_scoped:
            self.scope_overlay.enabled = False
            camera.fov = self.normal_fov

        # Refill ammo after reload duration finishes
        invoke(self._finish_reload, delay=self.reload_time)

    def _finish_reload(self):
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        print("Reload complete!")

    def toggle_scope(self, player_mesh):
        # Block scoping while reloading
        if self.is_reloading:
            return

        self.is_scoped = held_keys['right mouse']
        target_fov = self.scoped_fov if self.is_scoped else self.normal_fov
        
        camera.fov = lerp(camera.fov, target_fov, time.dt * 12)
        self.scope_overlay.enabled = self.is_scoped
        
        if player_mesh:
            player_mesh.enabled = not self.is_scoped
class AWP(Sniper):
    def __init__(self, model, scale, texture, texture_scale, model_name:str = "awp"):
        super().__init__(model=path.abspath(model), scale=scale, texture=path.abspath(texture), texture_scale=texture_scale, model_name=model_name)
class AK47(AutoGun):
    def __init__(self, model, scale, texture, texture_scale, model_name:str):
        super().__init__(model=path.abspath(model), scale=scale, texture=path.abspath(texture), texture_scale=texture_scale, model_name=model_name)
class Client(socket):
    def __init__(self, host: HostType, port: int):
        # Initialize standard TCP socket (AF_INET, SOCK_STREAM)
        super().__init__(AF_INET, SOCK_STREAM)
        # Client connects to the server address
        self.connect((host, port))
class Server(socket):
    def __init__(self, host: HostType, port: int):
        # Initialize standard TCP socket
        super().__init__(AF_INET, SOCK_STREAM)
        # Server binds to address and starts listening
        self.bind((host, port))
        self.listen(5)
class Wall(Base):
    def __init__(self, model:str, scale:str):
        super().__init__(model=model, scale=scale)
class Ground(Base):
    def __init__(self, model:str, texture:str, texture_scale:tuple, scale:tuple):
        model="plane"
        super().__init__(model=model, texture=path.abspath(texture), texture_scale=texture_scale, scale=scale)
class Sky(Base):
    def __init__(self, texture:str, model:str="plane"):
        super().__init__(model=model, position=(0, 2000, 0), texture=texture)
class Player(Base):
    def __init__(self, model:str, texture:str | None, **kwargs):
        super().__init__(
            model=model,
            texture=texture,
            **kwargs
        )
class Opponent(Base):
    def __init__(self,model,texture:str | None, **kwargs):
        super().__init__(
            model=model,
            texture=texture,
            **kwargs
        )
class AILoader:
    def __init__(self):
        # Nothing to do with this func so pass it
        pass
    def load_model(self):
        # Loads the qwen downloaded model.
        return lmstudio.llm("qwen/qwen3-1.7b")
class GetMoveBots:
    def __init__(self):
        self._model = AILoader().load_model()
        self._executor = ThreadPoolExecutor(max_workers=1)

    def fetch_move(self, prompt: str) -> Optional[MoveType]:
        """Runs synchronously inside a background worker thread."""
        response = self._model.respond(prompt)
        raw_text = response.content.upper()

        if "MOVE_FORWARD" in raw_text or "FORWARD" in raw_text:
            return MOVE_FLAGS[0]
        if "MOVE_LEFT" in raw_text or "LEFT" in raw_text:
            return MOVE_FLAGS[1]
        if "MOVE_RIGHT" in raw_text or "RIGHT" in raw_text:
            return MOVE_FLAGS[2]
        if "MOVE_BACKWARD" in raw_text or "BACKWARD" in raw_text:
            return MOVE_FLAGS[3]

        return None

    def request_move_async(self, prompt: str):
        """Dispatches request to background thread and returns a Future object."""
        return self._executor.submit(self.fetch_move, prompt)


class Bot(Base):
    def __init__(self, model_path: str, scale: tuple = (1, 1, 1), texture=None):
        super().__init__(
            model=os.path.abspath(model_path),
            texture=texture,
            scale=scale
        )
        self.moves_handler = GetMoveBots()
        
        # Track active future task
        self.current_future = None
        self.active_move: Optional[MoveType] = None
        self.move_timer = 0  # Duration bot executes move before asking again
        self.speed = 3.0

    def update(self):
        # 1. Start a new request if no request is running AND no active move is being performed
        if self.current_future is None and self.active_move is None:
            prompt = "You are a game bot. Action choices: MOVE_FORWARD, MOVE_LEFT, MOVE_RIGHT, MOVE_BACKWARD."
            # Submits task to thread pool asynchronously
            self.current_future = self.moves_handler.request_move_async(prompt)

        # 2. Check if the background thread has finished calculating
        if self.current_future is not None and self.current_future.done():
            # Retrieve the result from thread
            self.active_move = self.current_future.result()
            self.current_future = None  # Clear future so it can request again later
            self.move_timer = 0.5  # Move in chosen direction for 0.5 seconds

        # 3. Execute active move for a set duration (instead of just 1 frame)
        if self.active_move is not None:
            if self.active_move == MOVE_FORWARD:
                self.position += self.forward * self.speed * time.dt
            elif self.active_move == MOVE_LEFT:
                self.position += self.left * self.speed * time.dt
            elif self.active_move == MOVE_RIGHT:
                self.position += self.right * self.speed * time.dt
            elif self.active_move == MOVE_BACKWARD:
                self.position += self.back * self.speed * time.dt

            # Decrease move timer
            self.move_timer -= time.dt
            if self.move_timer <= 0:
                self.active_move = None  # Reset state -> triggers step 1 on next frame




        
