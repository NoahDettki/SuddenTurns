from Vector2 import Vector2
import pygame
import random

class Player:
    def __init__(self, player_setup, x, y, rotation):
        self.left_key = player_setup.left_key
        self.right_key = player_setup.right_key
        self.inactive_color = player_setup.inactive_color
        self.active_color = player_setup.active_color
        self.name = player_setup.name
        self.position = Vector2(x, y)
        self.direction = rotation
        self.speed = 90
        self.rotation_speed = 140
        self.radius = 4
        self.gap = False
        self.gap_time = 0.3
        self._gap_timer = 0
        self.min_time_without_gap = 1
        self.max_time_without_gap = 3
        self.alive = True
        self.score = 0

    def turn_left(self, delta_time):
        if self.alive:
            self.direction.rotate(-self.rotation_speed * delta_time)

    def turn_right(self, delta_time):
        if self.alive:
            self.direction.rotate(self.rotation_speed * delta_time)

    def move(self, delta_time):
        self.position = self.position + self.direction * self.speed * delta_time

    # The player leaves a trail behind. After a certain time or randomly a gap is
    # appearing in the trail. The trail starts again after a certain time.
    def update_gaps(self, delta_time):
        if self.gap:
            # Gap is active
            self._gap_timer -= delta_time
            if self._gap_timer <= 0:
                self.gap = False
                # How long until the next gap starts?
                self._gap_timer = random.uniform(self.min_time_without_gap, self.max_time_without_gap)
        else:
            # Trail is active
            self._gap_timer -= delta_time
            if self._gap_timer <= 0:
                self.gap = True
                # How long until the gap ends?
                self._gap_timer = self.gap_time
    
    def update(self, delta_time):
        if self.alive:
            self.move(delta_time)
            self.update_gaps(delta_time)

    def lose(self):
        self.alive = False

    def reset_to_starting_position(self, x, y, rotation):
        self.position = Vector2(x, y)
        self.direction = rotation
        self.radius = 4
        self.alive = True

class PlayerSetup:
    def __init__(self, inactive_color, active_color, left_key, right_key, name):
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.left_key = left_key
        self.right_key = right_key
        self.name = name