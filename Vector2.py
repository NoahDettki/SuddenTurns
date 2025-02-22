import numpy as np

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = np.array([x, y])

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    def rotate(self, angle_deg):
        angle_rad = np.radians(angle_deg)
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad),  np.cos(angle_rad)]
        ])
        self.value = rotation_matrix @ self.value
        self.x = self.value[0]
        self.y = self.value[1]
    
    def normalize(self):
        norm = np.linalg.norm(self.value)
        if norm != 0:
            self.value = self.value / norm
        self.x = self.value[0]
        self.y = self.value[1]