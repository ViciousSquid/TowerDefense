import math

class Projectile:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 10

    def update(self):
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def hit_target(self):
        distance = math.sqrt((self.x - self.target.x)**2 + (self.y - self.target.y)**2)
        return distance < 15  # Enemy radius
