from random import randint, uniform

import pygame
import pymunk as pm
from pymunk import Vec2d

import src.settings as s
from src.graphics import SpriteSheet


class ActorAdult(pygame.sprite.Sprite):
    def __init__(self, pos, sprite_sheets, space, static_pivot=True):
        # pymunk stuff
        self.body = pm.Body(mass=1, moment=pm.inf, body_type=pm.Body.DYNAMIC)
        pm_x, pm_y = s.flip_y(pos)
        pm_size_x, pm_size_y = s.ADULT_ACTOR_SIZE
        self.body.position = pm_x + pm_size_x // 2, pm_y - pm_size_y // 2  # body.position == rect.center
        self.shape = pm.Poly.create_box(self.body, s.ADULT_ACTOR_SIZE)
        self.shape.elasticity = 0
        self.shape.friction = 1
        space.add(self.body, self.shape)

        if static_pivot is True:
            pivot = self.create_pivot(space.static_body)
            space.add(pivot)

        # pygame stuff
        super(ActorAdult, self).__init__()

        sh = {key: SpriteSheet(value) for key, value in sprite_sheets.items()}

        self.images = []
        for x in sh:
            self.images_temp = []
            for i in range(4):
                self.images_temp.append(sh[x].get_image(i))
            self.images.append(self.images_temp)

        # Just to reference what type self.image should be
        self.image = sh["IDLE"].get_image(0)
        pygame.transform.scale(self.image, s.ADULT_ACTOR_SIZE)

        self.rect = self.image.get_rect(topleft=pos)
        self.state = {
            "ATTACK": 0,
            "DEATH": 1,
            "HURT": 2,
            "IDLE": 3,
            "WALK": 4
        }
        self.current_state = 4
        self.anim_type = 0
        self.anim_delay = 0.2
        self.time_in_frame = 0.0

        self.directionx, self.directiony = 0, 0
        self.vel = 5

        self.time_to_change_dir = 0.0
        self.dir_delay = 0.5

    def create_pivot(self, control_body):
        """Emulate linear friction"""
        pivot = pm.PivotJoint(control_body, self.body, (0, 0), (0, 0))
        pivot.max_bias = 0  # disable joint correction
        pivot.max_force = 1000
        return pivot

    def move(self):
        self.rect.x += self.vel * self.directionx
        self.rect.y += self.vel * self.directiony

    # Needs to be updated i will fix it later
    def update_directions(self, time_delta):
        """
        -1: Left / Up
        0: No movement
        1: Right / Down
        """
        self.time_to_change_dir += time_delta
        if self.time_to_change_dir > self.dir_delay:
            # So they walk random distances
            self.dir_delay = uniform(0.05, 0.5)
            # print(self.dir_delay)

            self.directionx = randint(-1, 1)
            self.directiony = randint(-1, 1)
            self.time_to_change_dir = 0.0

    def synchronize_rect_body(self):
        """Synchronizes player rect with pymunk player shape"""
        self.rect.center = s.flip_y(self.body.position)

    def update(self, time_delta, *args):
        self.time_in_frame += time_delta

        self.synchronize_rect_body()

        for state in self.state.values():
            if self.current_state == state:
                self.image = self.images[self.current_state][self.anim_type]
                if self.time_in_frame > self.anim_delay:
                    # Temporarly called from here
                    self.update_directions(time_delta)
                    self.move()

                    self.anim_type = (self.anim_type + 1) if self.anim_type < 3 else 0
                    self.time_in_frame = 0


"""
    def update(self):
        self.image = self.images[self.state["WALK"]][self.anim_type]
        self.anim_type = (self.anim_type + 1) if self.anim_type < 3 else 0
"""


class TestActor(ActorAdult):
    """Test actor for physics tests"""
    def __init__(self, pos, sprite_sheets, space):
        # physics stuff
        super(TestActor, self).__init__(pos, sprite_sheets, space, static_pivot=False)
        self.vel = 30
        self.shape.color = (255, 0, 0, 0)

        self.control_body = pm.Body(body_type=pm.Body.KINEMATIC)
        self.control_body.position = self.body.position
        space.add(self.control_body)

        pivot = self.create_pivot(self.control_body)
        space.add(pivot)

        self.target_position = None

    def select_target(self, target_pos):
        self.target_position = s.flip_y(target_pos)

    def handle_mouse_event(self, type, pos):
        if type == pygame.MOUSEMOTION:
            self.handle_mouse_move(pos)
        elif type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(pos)
        elif type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(pos)

    def handle_mouse_move(self, pos):
        pass

    def handle_mouse_down(self, pos):
        self.select_target(pos)

    def handle_mouse_up(self, pos):
        pass

    def update(self, time_delta, *args):
        super(TestActor, self).update(time_delta, *args)
        self.synchronize_rect_body()  # yes, need to call it twice :(

        if self.target_position is not None:

            target_delta = self.target_position - self.body.position
            if target_delta.get_length_sqrd() < self.vel ** 2:
                self.control_body.velocity = 0, 0
            else:

                # Left-right direction
                if self.target_position[0] > int(self.body.position.x):
                    dir_lr = 1
                elif self.target_position[0] < int(self.body.position.x):
                    dir_lr = -1
                else:
                    dir_lr = 0

                # Up-down direction
                if self.target_position[1] < int(self.body.position.y):
                    dir_ud = -1
                elif self.target_position[1] > int(self.body.position.y):
                    dir_ud = 1
                else:
                    dir_ud = 0

                dv = Vec2d(self.vel * dir_lr, self.vel * dir_ud)
                self.control_body.velocity = self.body.rotation_vector.cpvrotate(dv)
