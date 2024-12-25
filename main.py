import tkinter as tkinter
from tkinter import ttk, messagebox, simpledialog
import json
import math
from PIL import Image, ImageTk, ImageDraw
import time
import os
from PIL import ImageGrab

class TowerDefenseGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tower Defense Game")

        # Game constants
        self.CANVAS_WIDTH = 800
        self.CANVAS_HEIGHT = 600
        self.GRID_SIZE = 50
        self.TOWER_COST = 100
        self.UPGRADE_COST = 150  # Cost to upgrade a tower

        # Wave configuration
        self.WAVE_COOLDOWN = 10000  # 10 seconds between waves
        self.SPAWN_INTERVAL = 2000  # 2 seconds between enemies
        self.ENEMIES_PER_WAVE = 5  # Starting number of enemies per wave
        self.ENEMY_HEALTH_INCREASE = 20  # Health increase per wave
        self.ENEMY_SPEED_INCREASE = 0.2  # Speed increase per wave

        # Game state
        self.editor_mode = False
        self.selected_tool = "path"
        self.money = 500
        self.score = 0
        self.lives = 10
        self.wave = 1
        self.enemy_path = []
        self.towers = []
        self.enemies = []
        self.projectiles = []

        # Wave management
        self.wave_in_progress = False
        self.enemies_spawned = 0
        self.enemies_defeated = 0
        self.last_spawn_time = 0
        self.wave_cooldown_start = 0
        self.wave_status = "Ready to start"
        self.game_paused = False
        self.game_over = False  # New attribute to track game over state

        # Settings
        self.show_enemy_health = True  # Toggle for showing enemy health

        # Tower selection
        self.selected_tower = None  # Track the currently selected tower

        # Start and End entities
        self.start_entity = None
        self.end_entity = None

        self.setup_user_interface()
        self.load_images()
        self.setup_bindings()
        self.game_loop()

    def setup_user_interface(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=5, pady=5)

        # Top control panel
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill='x', pady=5)

        # Game stats
        self.stats_frame = ttk.Frame(self.control_frame)
        self.stats_frame.pack(side='left', padx=5)

        self.money_label = ttk.Label(self.stats_frame, text=f"Money: ${self.money}")
        self.money_label.pack(side='left', padx=5)

        self.lives_label = ttk.Label(self.stats_frame, text=f"Lives: {self.lives}")
        self.lives_label.pack(side='left', padx=5)

        self.score_label = ttk.Label(self.stats_frame, text=f"Score: {self.score}")
        self.score_label.pack(side='left', padx=5)

        self.wave_label = ttk.Label(self.stats_frame, text=f"Wave: {self.wave}")
        self.wave_label.pack(side='left', padx=5)

        # Add wave status label
        self.wave_status_label = ttk.Label(self.stats_frame, text=self.wave_status)
        self.wave_status_label.pack(side='left', padx=5)

        # Control buttons
        self.button_frame = ttk.Frame(self.control_frame)
        self.button_frame.pack(side='right', padx=5)

        self.editor_button = ttk.Button(self.button_frame, text="Toggle Editor", command=self.toggle_editor)
        self.editor_button.pack(side='left', padx=2)

        self.save_button = ttk.Button(self.button_frame, text="Save Level", command=self.save_level)
        self.save_button.pack(side='left', padx=2)

        self.load_button = ttk.Button(self.button_frame, text="Load Level", command=self.load_level)
        self.load_button.pack(side='left', padx=2)

        self.pause_button = ttk.Button(self.button_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side='left', padx=2)

        # Add start wave button with dark green background and bigger text
        self.start_wave_button = tkinter.Button(self.button_frame, text="Start Wave", command=self.start_wave,
                                                bg='darkgreen', fg='white', font=("Arial", 12, "bold"))
        self.start_wave_button.pack(side='left', padx=2)

        # Add upgrade tower button
        # self.upgrade_button = ttk.Button(self.button_frame, text="Upgrade Tower", command=self.upgrade_tower)
        # self.upgrade_button.pack(side='left', padx=2)

        # Game canvas
        self.canvas = tkinter.Canvas(self.main_frame, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg='lightgreen')
        self.canvas.pack(expand=True, fill='both')

        # Editor tools
        self.tools_frame = ttk.LabelFrame(self.main_frame, text="Editor Tools", height=50)
        self.tools_frame.pack(fill='x', pady=5)

        # Path Tool button with blue background and bold text
        self.path_button = tkinter.Button(self.tools_frame, text="Path", command=lambda: self.set_tool("path"),
                                          bg='red', fg='white', font=("Arial", 10, "bold"))
        self.path_button.pack(side='left', padx=5)

        # Tower Tool button with blue background and bold text
        self.tower_button = tkinter.Button(self.tools_frame, text="Tower", command=lambda: self.set_tool("tower"),
                                           bg='blue', fg='white', font=("Arial", 10, "bold"))
        self.tower_button.pack(side='left', padx=5)

        # Start Tool button with yellow background and bold text
        self.start_button = tkinter.Button(self.tools_frame, text="Start", command=lambda: self.set_tool("start"),
                                           bg='yellow', fg='black', font=("Arial", 10, "bold"))
        self.start_button.pack(side='left', padx=5)

        # End Tool button with yellow background and bold text
        self.end_button = tkinter.Button(self.tools_frame, text="End", command=lambda: self.set_tool("end"),
                                         bg='yellow', fg='black', font=("Arial", 10, "bold"))
        self.end_button.pack(side='left', padx=5)

        self.clear_button = ttk.Button(self.tools_frame, text="Clear All", command=self.clear_level)
        self.clear_button.pack(side='left', padx=5)

        self.tools_frame.pack_forget()  # Hide tools initially

        # Settings menu
        self.settings_menu = tkinter.Menu(self.root)
        self.root.config(menu=self.settings_menu)

        self.view_menu = tkinter.Menu(self.settings_menu, tearoff=0)
        self.settings_menu.add_cascade(label="Settings", menu=self.view_menu)
        self.view_menu.add_checkbutton(label="Don't Show Enemy Health", command=self.toggle_enemy_health_visibility,
                                       variable=tkinter.BooleanVar(value=self.show_enemy_health))

        # Add the 'Help' menu
        self.help_menu = tkinter.Menu(self.settings_menu, tearoff=0)
        self.settings_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

    def load_images(self):
        # Create placeholder images
        self.tower_image = self.create_circle_image(25, 'blue')
        self.enemy_image = self.create_circle_image(15, 'red')
        self.projectile_image = self.create_circle_image(5, 'yellow')

        # Load the path sprite image
        self.path_image = Image.open("path.jpg")
        self.path_image = ImageTk.PhotoImage(self.path_image)

    def create_circle_image(self, radius, color):
        # Create a circular image using PIL
        size = radius * 2
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        return ImageTk.PhotoImage(image)

    def setup_bindings(self):
        self.canvas.bind('<Button-1>', self.canvas_clicked)
        self.canvas.bind('<Motion>', self.update_preview)

    def canvas_clicked(self, event):
        if not self.editor_mode:
            return

        x, y = event.x, event.y
        if self.selected_tool == "path":
            self.enemy_path.append((x, y))
            self.draw_path()
        elif self.selected_tool == "tower" and self.money >= self.TOWER_COST:
            # Snap to grid
            grid_x = round(x / self.GRID_SIZE) * self.GRID_SIZE
            grid_y = round(y / self.GRID_SIZE) * self.GRID_SIZE

            # Check if tower already exists at this location
            for tower in self.towers:
                if tower.x == grid_x and tower.y == grid_y:
                    return

            self.towers.append(Tower(grid_x, grid_y))
            self.money -= self.TOWER_COST
            self.update_labels()
        elif self.selected_tool == "start":
            if self.start_entity:
                self.canvas.delete(self.start_entity)
            self.start_entity = self.canvas.create_polygon(
                x - 25, y + 15, x, y - 25, x + 25, y + 15,
                fill='yellow', outline='black', tags='start'
            )
            self.canvas.create_text(
                x + 2, y + 2, text='S', fill='black', font=("Arial", 16, "bold"), tags='start'
            )
            self.canvas.create_text(
                x, y, text='S', fill='black', font=("Arial", 16, "bold"), tags='start'
            )
            self.start_position = (x, y)
        elif self.selected_tool == "end":
            if self.end_entity:
                self.canvas.delete(self.end_entity)
            self.end_entity = self.canvas.create_polygon(
                x - 25, y - 15, x, y + 25, x + 25, y - 15,
                fill='yellow', outline='black', tags='end'
            )
            self.canvas.create_text(
                x + 2, y + 2, text='E', fill='black', font=("Arial", 16, "bold"), tags='end'
            )
            self.canvas.create_text(
                x, y, text='E', fill='black', font=("Arial", 16, "bold"), tags='end'
            )
            self.end_position = (x, y)
        else:
            # Check if a tower is clicked for selection
            for tower in self.towers:
                # Check if the click is within the tower's bounding box
                if (tower.x - 25 <= x <= tower.x + 25 and
                    tower.y - 25 <= y <= tower.y + 25):
                    self.select_tower(tower)
                    return

    def update_preview(self, event):
        if not self.editor_mode:
            return

        self.canvas.delete('preview')
        if self.selected_tool == "tower":
            grid_x = round(event.x / self.GRID_SIZE) * self.GRID_SIZE
            grid_y = round(event.y / self.GRID_SIZE) * self.GRID_SIZE
            self.canvas.create_oval(
                grid_x - 25, grid_y - 25,
                grid_x + 25, grid_y + 25,
                outline='blue', tags='preview'
            )

    def toggle_editor(self):
        self.editor_mode = not self.editor_mode
        if self.editor_mode:
            self.tools_frame.pack(fill='x', pady=5)
            self.pause_button.config(state='disabled')
            self.game_paused = True
            self.draw_arrows_on_path()  # Start drawing arrows
        else:
            self.tools_frame.pack_forget()
            self.pause_button.config(state='normal')
            self.game_paused = False
            self.canvas.delete('arrow')  # Clear arrows when exiting editor mode

    def set_tool(self, tool):
        self.selected_tool = tool

    def save_level(self):
        level_name = simpledialog.askstring("Save Level", "Enter a name for the level:")
        if not level_name:
            return

        level_data = {
            "path": self.enemy_path,
            "towers": [(tower.x, tower.y) for tower in self.towers],
            "start": self.start_position,
            "end": self.end_position
        }

        # Create the levels folder if it doesn't exist
        if not os.path.exists("levels"):
            os.makedirs("levels")

        # Save the level data
        level_file = os.path.join("levels", f"{level_name}.json")
        with open(level_file, "w") as f:
            json.dump(level_data, f)

        # Generate a thumbnail programmatically
        thumbnail = self.create_level_thumbnail(level_data)
        thumbnail.save(os.path.join("levels", f"{level_name}_thumb.png"))

        messagebox.showinfo("Success", "Level saved successfully!")

    def create_level_thumbnail(self, level_data):
        # Create a blank 128x128 thumbnail image
        thumbnail = Image.new("RGB", (128, 128), "white")
        draw = ImageDraw.Draw(thumbnail)

        # Scale the level data to fit the thumbnail
        scale_factor = 128 / max(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)

        # Draw the path
        path = level_data["path"]
        if len(path) > 1:
            scaled_path = [(x * scale_factor, y * scale_factor) for x, y in path]
            draw.line(scaled_path, fill="blue", width=2)

        # Draw the START position
        start_x, start_y = level_data["start"]
        scaled_start = (start_x * scale_factor, start_y * scale_factor)
        draw.polygon(
            [
                (scaled_start[0] - 5, scaled_start[1] + 5),
                (scaled_start[0], scaled_start[1] - 5),
                (scaled_start[0] + 5, scaled_start[1] + 5),
            ],
            fill="yellow",
            outline="black",
        )
        draw.text(scaled_start, "S", fill="black", anchor="mm")

        # Draw the END position
        end_x, end_y = level_data["end"]
        scaled_end = (end_x * scale_factor, end_y * scale_factor)
        draw.polygon(
            [
                (scaled_end[0] - 5, scaled_end[1] - 5),
                (scaled_end[0], scaled_end[1] + 5),
                (scaled_end[0] + 5, scaled_end[1] - 5),
            ],
            fill="yellow",
            outline="black",
        )
        draw.text(scaled_end, "E", fill="black", anchor="mm")

        # Draw the towers
        for tower_x, tower_y in level_data["towers"]:
            scaled_tower = (tower_x * scale_factor, tower_y * scale_factor)
            draw.ellipse(
                (
                    scaled_tower[0] - 4,
                    scaled_tower[1] - 4,
                    scaled_tower[0] + 4,
                    scaled_tower[1] + 4,
                ),
                fill="blue",
                outline="black",
            )

        return thumbnail

    def load_level(self):
        # Create the levels folder if it doesn't exist
        if not os.path.exists("levels"):
            os.makedirs("levels")

        # Get all level files
        level_files = [f for f in os.listdir("levels") if f.endswith(".json")]

        if not level_files:
            messagebox.showinfo("Info", "No levels available to load.")
            return

        # Create a new window to display the levels
        load_window = tkinter.Toplevel(self.root)
        load_window.title("Load Level")

        # Create a frame to hold the level thumbnails and names
        level_frame = ttk.Frame(load_window)
        level_frame.pack(fill='both', expand=True)

        # Load and display each level with its thumbnail
        for level_file in level_files:
            level_name = level_file.replace(".json", "")
            thumbnail_path = os.path.join("levels", f"{level_name}_thumb.png")

            if os.path.exists(thumbnail_path):
                thumbnail = Image.open(thumbnail_path)
                thumbnail = thumbnail.resize((128, 128), Image.Resampling.LANCZOS)  # Ensure thumbnail is 128x128
                thumbnail = ImageTk.PhotoImage(thumbnail)

                # Create a button with the thumbnail
                level_button = ttk.Button(level_frame, image=thumbnail, text=level_name, compound=tkinter.BOTTOM,
                                         command=lambda lf=level_file: self.load_selected_level(lf, load_window))
                level_button.image = thumbnail  # Keep a reference to avoid garbage collection
                level_button.pack(side='left', padx=5, pady=5)

    def load_selected_level(self, level_file, load_window):
        try:
            with open(os.path.join("levels", level_file), "r") as f:
                level_data = json.load(f)
                self.enemy_path = level_data["path"]
                self.towers = [Tower(x, y) for x, y in level_data["towers"]]
                self.start_position = level_data["start"]
                self.end_position = level_data["end"]
                self.draw_path()
                self.draw_start_end()
            messagebox.showinfo("Success", "Level loaded successfully!")
            load_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load level: {str(e)}")

    def clear_level(self):
        self.enemy_path = []
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.start_entity = None
        self.end_entity = None
        self.canvas.delete('all')

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        self.pause_button.config(text="Resume" if self.game_paused else "Pause")

    def update_labels(self):
        self.money_label.config(text=f"Money: ${self.money}")
        self.lives_label.config(text=f"Lives: {self.lives}")
        self.score_label.config(text=f"Score: {self.score}")
        self.wave_label.config(text=f"Wave: {self.wave}")

    def draw_path(self):
        self.canvas.delete('path')
        if len(self.enemy_path) > 1:
            # Calculate the total length of the path
            total_length = 0
            for i in range(len(self.enemy_path) - 1):
                x1, y1 = self.enemy_path[i]
                x2, y2 = self.enemy_path[i + 1]
                dx = x2 - x1
                dy = y2 - y1
                total_length += math.sqrt(dx**2 + dy**2)

            # Place sprites along the path at regular intervals
            sprite_interval = 40  # Distance between sprites (adjust as needed)
            num_sprites = int(total_length / sprite_interval)

            # Draw sprites along the path
            for i in range(num_sprites):
                t = i / num_sprites
                # Interpolate the position along the path
                x, y = self.interpolate_path(t)
                self.canvas.create_image(x, y, image=self.path_image, tags='path')

    def interpolate_path(self, t):
        """
        Interpolate the position along the path based on a parameter t (0 to 1).
        """
        if len(self.enemy_path) < 2:
            return self.enemy_path[0] if self.enemy_path else (0, 0)

        # Calculate the total length of the path
        total_length = 0
        segment_lengths = []
        for i in range(len(self.enemy_path) - 1):
            x1, y1 = self.enemy_path[i]
            x2, y2 = self.enemy_path[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            segment_length = math.sqrt(dx**2 + dy**2)
            segment_lengths.append(segment_length)
            total_length += segment_length

        # Find the segment where the interpolated point lies
        target_length = t * total_length
        accumulated_length = 0
        for i in range(len(self.enemy_path) - 1):
            x1, y1 = self.enemy_path[i]
            x2, y2 = self.enemy_path[i + 1]
            segment_length = segment_lengths[i]
            if accumulated_length + segment_length >= target_length:
                # Interpolate within this segment
                segment_t = (target_length - accumulated_length) / segment_length
                x = x1 + (x2 - x1) * segment_t
                y = y1 + (y2 - y1) * segment_t
                return x, y
            accumulated_length += segment_length

        # If t == 1, return the last point
        return self.enemy_path[-1]

    def start_wave(self):
        if not self.wave_in_progress and not self.game_paused and not self.editor_mode:
            self.wave_in_progress = True
            self.enemies_spawned = 0
            self.enemies_defeated = 0
            self.wave_status = f"Wave {self.wave} in progress"
            self.update_wave_status()
            self.start_wave_button.config(state='disabled')

    def update_wave_status(self):
        if self.wave_in_progress:
            progress = f"({self.enemies_defeated}/{self.ENEMIES_PER_WAVE})"
            self.wave_status_label.config(text=f"{self.wave_status} {progress}")
        else:
            if self.wave_cooldown_start > 0:
                remaining = (self.WAVE_COOLDOWN - (time.time() * 1000 - self.wave_cooldown_start)) / 1000
                if remaining > 0:
                    self.wave_status_label.config(text=f"Next wave in {remaining:.1f}s")
                else:
                    self.wave_status_label.config(text="Ready to start next wave")
            else:
                self.wave_status_label.config(text=self.wave_status)

    def spawn_enemy(self):
        if (self.wave_in_progress and
            self.enemies_spawned < self.ENEMIES_PER_WAVE and
            time.time() * 1000 - self.last_spawn_time >= self.SPAWN_INTERVAL):

            # Create enemy with increased stats based on wave number
            enemy = Enemy(self.enemy_path, self.start_position, self.end_position)
            enemy.health += (self.wave - 1) * self.ENEMY_HEALTH_INCREASE
            enemy.speed += (self.wave - 1) * self.ENEMY_SPEED_INCREASE

            self.enemies.append(enemy)
            self.enemies_spawned += 1
            self.last_spawn_time = time.time() * 1000

    def check_wave_completion(self):
        if (self.wave_in_progress and
            self.enemies_spawned >= self.ENEMIES_PER_WAVE and
            len(self.enemies) == 0):

            self.wave_in_progress = False
            self.wave += 1
            self.ENEMIES_PER_WAVE += 2  # Increase enemies per wave
            self.wave_cooldown_start = time.time() * 1000
            self.wave_status = "Wave completed!"

            # Give wave completion bonus
            wave_bonus = self.wave * 100
            self.money += wave_bonus
            self.score += wave_bonus

            messagebox.showinfo("Wave Complete",
                                f"Wave {self.wave-1} completed!\nBonus: ${wave_bonus}")

    def toggle_enemy_health_visibility(self):
        self.show_enemy_health = not self.show_enemy_health

    def game_loop(self):
        if self.game_over:
            return

        if not self.game_paused and not self.editor_mode:
            # Check wave cooldown
            if (not self.wave_in_progress and
                self.wave_cooldown_start > 0 and
                time.time() * 1000 - self.wave_cooldown_start >= self.WAVE_COOLDOWN):

                self.wave_cooldown_start = 0
                self.start_wave_button.config(state='normal')

            self.spawn_enemy()

            # Update game objects
            for enemy in self.enemies[:]:
                enemy.update()
                if enemy.reached_end:
                    self.enemies.remove(enemy)
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        messagebox.showinfo("Game Over", f"Final Score: {self.score}")
                        self.root.quit()
                        return
                elif enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.enemies_defeated += 1
                    self.money += 25
                    self.score += 100

            for tower in self.towers:
                tower.update(self.enemies)
                if tower.can_shoot:
                    closest_enemy = tower.get_closest_enemy(self.enemies)
                    if closest_enemy:
                        self.projectiles.append(Projectile(tower.x, tower.y, closest_enemy))
                        tower.last_shot = time.time()

            for projectile in self.projectiles[:]:
                projectile.update()
                if projectile.hit_target():
                    projectile.target.health -= 10
                    self.projectiles.remove(projectile)

            self.check_wave_completion()
            self.update_wave_status()
            self.update_labels()

        # Clear and redraw
        self.canvas.delete('game_object')

        # Draw towers
        for tower in self.towers:
            # Draw the base of the tower
            self.canvas.create_oval(
                tower.x - 25, tower.y - 25,
                tower.x + 25, tower.y + 25,
                fill='blue', tags='game_object'
            )

            # Draw the rotating turret
            turret_length = 20
            turret_end_x = tower.x + turret_length * math.cos(math.radians(tower.turret_angle))
            turret_end_y = tower.y + turret_length * math.sin(math.radians(tower.turret_angle))
            self.canvas.create_line(
                tower.x, tower.y,
                turret_end_x, turret_end_y,
                fill='white', width=4, tags='game_object'
            )

            # Draw the tower level
            self.canvas.create_text(
                tower.x, tower.y,
                text=str(tower.level),
                fill='white',
                font=("Arial", 12),
                tags='game_object'
            )

        # Draw enemies
        for enemy in self.enemies:
            self.canvas.create_oval(
                enemy.x - 15, enemy.y - 15,
                enemy.x + 15, enemy.y + 15,
                fill='red', tags='game_object'
            )
            if self.show_enemy_health:
                health_percentage = int((enemy.health / 100) * 100)  # Assuming base health is 100
                # Draw drop shadow
                self.canvas.create_text(
                    enemy.x + 1, enemy.y - 19,  # Slightly offset
                    text=f"{health_percentage}%",
                    fill='black',
                    font=("Arial", 8),
                    tags='game_object'
                )
                # Draw actual health text
                self.canvas.create_text(
                    enemy.x, enemy.y - 20,  # Position above the enemy
                    text=f"{health_percentage}%",
                    fill='white',
                    font=("Arial", 8),
                    tags='game_object'
                )

        # Draw projectiles
        for projectile in self.projectiles:
            self.canvas.create_oval(
                projectile.x - 5, projectile.y - 5,
                projectile.x + 5, projectile.y + 5,
                fill='yellow', tags='game_object'
            )

        self.root.after(16, self.game_loop)  # ~60 FPS

    def upgrade_tower(self):
        if self.selected_tower and self.money >= self.UPGRADE_COST:
            self.selected_tower.upgrade()
            self.money -= self.UPGRADE_COST
            self.update_labels()
            messagebox.showinfo("Upgrade", f"Tower upgraded!\nDamage: {self.selected_tower.damage}, Range: {self.selected_tower.range}")
            # Remove the highlight after upgrading
            self.canvas.delete('selected_tower')
            self.selected_tower = None
        else:
            messagebox.showerror("Error", "Not enough money to upgrade tower or no tower selected!")

    def select_tower(self, tower):
        self.selected_tower = tower
        messagebox.showinfo("Tower Selected", f"Tower at ({tower.x}, {tower.y}) selected for upgrade.")
        # Highlight the selected tower
        self.canvas.delete('selected_tower')  # Clear previous highlight
        self.canvas.create_oval(
            tower.x - 27, tower.y - 27,
            tower.x + 27, tower.y + 27,
            outline='yellow', width=3, tags='selected_tower'
        )

    def draw_start_end(self):
        if self.start_entity:
            self.canvas.delete(self.start_entity)
        if self.end_entity:
            self.canvas.delete(self.end_entity)

        if self.start_position:
            x, y = self.start_position
            self.start_entity = self.canvas.create_polygon(
                x - 25, y + 15, x, y - 25, x + 25, y + 15,
                fill='yellow', outline='black', tags='start'
            )
            self.canvas.create_text(
                x + 2, y + 2, text='S', fill='black', font=("Arial", 16, "bold"), tags='start'
            )
            self.canvas.create_text(
                x, y, text='S', fill='black', font=("Arial", 16, "bold"), tags='start'
            )

        if self.end_position:
            x, y = self.end_position
            self.end_entity = self.canvas.create_polygon(
                x - 25, y - 15, x, y + 25, x + 25, y - 15,
                fill='yellow', outline='black', tags='end'
            )
            self.canvas.create_text(
                x + 2, y + 2, text='E', fill='black', font=("Arial", 16, "bold"), tags='end'
            )
            self.canvas.create_text(
                x, y, text='E', fill='black', font=("Arial", 16, "bold"), tags='end'
            )

    def draw_arrows_on_path(self):
        if not self.editor_mode:
            return

        # Clear previous arrows
        self.canvas.delete('arrow')

        # Draw arrows along the path
        if len(self.enemy_path) > 1:
            num_arrows = 1  # Number of arrows to draw
            for i in range(num_arrows):
                t = (i / num_arrows) + (time.time() % 1)  # Animate arrows smoothly
                if t >= 1:
                    t -= 1

                # Get the position on the path
                x, y = self.interpolate_path(t)

                # Get the direction of the path at this point
                if t < 1:
                    next_x, next_y = self.interpolate_path(t + 0.01)
                    dx = next_x - x
                    dy = next_y - y
                    angle = math.degrees(math.atan2(dy, dx))

                    # Draw the arrow
                    self.canvas.create_line(
                        x, y, x + dx * 10, y + dy * 10,
                        arrow=tkinter.LAST, fill='black', width=2, tags='arrow'
                    )

        # Schedule the next update
        self.root.after(100, self.draw_arrows_on_path)

    def show_about(self):
        messagebox.showinfo("About", "Tower Defense\nVersion 1.0\ngithub.com/ViciousSquid")

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

class Enemy:
    def __init__(self, path, start_position, end_position):
        self.path = path
        self.current_point = 0
        self.x, self.y = start_position
        self.speed = 2  # Base speed
        self.health = 100  # Base health
        self.reached_end = False
        self.end_position = end_position

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

if __name__ == "__main__":
    root = tkinter.Tk()
    game = TowerDefenseGame(root)
    root.mainloop()