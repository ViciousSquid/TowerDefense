# enemy.py
import math

class Enemy:
    def __init__(self, path, start_position, end_position, is_rare=False):
        self.path = path
        self.current_point = 0
        self.x, self.y = start_position
        self.speed = 2  # Base speed
        self.health = 100  # Base health
        self.reached_end = False
        self.end_position = end_position
        self.is_rare = is_rare  # Is Rare enemy?
        if self.is_rare:
            self.health *= 1.25  # 125% health for rare enemies
            self.size_multiplier = 1.5  # 50% bigger
        else:
            self.size_multiplier = 1  # Default size

    def update(self):
        if self.current_point < len(self.path) - 1:
            # Move toward the next point in the path
            target_x, target_y = self.path[self.current_point + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.speed:
                # If close enough to the next point, move to the next point
                self.current_point += 1
                self.x, self.y = self.path[self.current_point]
            else:
                # Move toward the next point
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        else:
            # Move toward the end position
            end_x, end_y = self.end_position
            dx = end_x - self.x
            dy = end_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.speed:
                self.reached_end = True
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
