import pygame

class Keyboard:
    def __init__(self):
        self.keys = {}
        self.keys_pressed = set()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key not in self.keys or not self.keys[event.key]:
                self.keys_pressed.add(event.key)
            self.keys[event.key] = True
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False

    def is_key_down(self, key):
        return self.keys.get(key, False)

    def was_key_pressed(self, key):
        return key in self.keys_pressed

    def reset_frame_state(self):
        self.keys_pressed.clear()