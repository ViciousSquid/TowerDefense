import time
import math

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.damage = 10
        self.fire_rate = 1.0  # seconds
        self.last_shot = 0
        self.level = 1
        self.turret_angle = 0  # Initial turret angle

    def update(self, enemies):
        self.can_shoot = time.time() - self.last_shot >= self.fire_rate
        self.track_enemy(enemies)  # Update turret angle to track the closest enemy

    def get_closest_enemy(self, enemies):
        closest = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if dist < self.range and dist < min_dist:
                closest = enemy
                min_dist = dist
        return closest

    def track_enemy(self, enemies):
        closest_enemy = self.get_closest_enemy(enemies)
        if closest_enemy:
            # Calculate the angle to the closest enemy
            dx = closest_enemy.x - self.x
            dy = closest_enemy.y - self.y
            self.turret_angle = math.degrees(math.atan2(dy, dx))

    def upgrade(self):
        self.level += 1
        self.damage += 5  # Increase damage
        self.range += 25  # Increase range
