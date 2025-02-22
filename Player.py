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
        self.speed = 1.4/2
        self.rotation_speed = 2.5/2
        self.radius = 4
        self.gap = False
        self.gap_time = 0.29
        self._gap_timer = 0
        self.max_time_without_gap = 3
        self.gap_propability = 0.01
        self.alive = True
        self.score = 0

    def turn_left(self):
        if self.alive:
            self.direction.rotate(-self.rotation_speed)

    def turn_right(self):
        if self.alive:
            self.direction.rotate(self.rotation_speed)

    def move(self):
        if self.alive:
            self.position = self.position + self.direction * self.speed

    # The player leaves a trail behind. After a certain time or randomly a gap is
    # appearing in the trail. The trail starts again after a certain time.
    def update_gaps(self, time):
        if self.gap:
            # Gap is active
            self._gap_timer -= time
            if self._gap_timer <= 0:
                self.gap = False
                self._gap_timer = self.max_time_without_gap
        else:
            # Trail is active
            self._gap_timer -= time
            if random.random() < self.gap_propability or self._gap_timer <= 0:
                self.gap = True
                self._gap_timer = self.gap_time

    def lose(self):
        self.alive = False

    def reset_to_starting_position(self, x, y, rotation):
        self.position = Vector2(x, y)
        self.direction = rotation
        self.alive = True

class PlayerSetup:
    def __init__(self, inactive_color, active_color, left_key, right_key, name):
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.left_key = left_key
        self.right_key = right_key
        self.name = name