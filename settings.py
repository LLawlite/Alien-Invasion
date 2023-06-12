# A class to sotre all settings for Alien Invasion
class Settings:

    def __init__(self):
        #Initialize the game setting;s static setting

        #Screen Setting
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color=(13, 12, 12)

        # Ship settings
        self.ship_limit=2

        # Bullet settings
        self.bullet_width=3
        self.bullet_height=15
        self.bullet_color= (255, 255, 255)
        self.bullet_allowed=3

        # Alien settings
        self.fleet_drop_speed = 10

        # How quicky the game speeds up
        self.speedup_scale = 1.1

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """ Initialize the settings that change thropught the game """
        self.ship_speed= 1.5
        self.bullet_speed= 3.0
        self.alien_speed = 1.0

        # fleed direction of 1 represents right and -1 represents left
        self.fleet_direction =1

        # Scoring
        self.alien_points = 50

    def increase_seed(self):
        """ Increase speed settings """
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale



