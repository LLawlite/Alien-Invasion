import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """overall class to manage game assests and behavior."""

    def __init__(self):
        """ Initialize the game and create game resources."""
        pygame.init()

        self.settings=Settings()


        self.screen=pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width=self.screen.get_rect().width
        self.settings.screen_height=self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")



        # Create an instance to store game statics and create a scoreboard
        self.stats=GameStats(self)
        self.sb=Scoreboard(self)


        self.ship=Ship(self)
        self.bullets=pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Make the paly button
        self.play_button=Button(self,"Play")


    def run_game(self):
        """Start the main loop for the game"""

        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()






    def _check_events(self):
        # wathc for keyboard and mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos= pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self,mouse_pos):
        """ Start a new game when player click play """
        button_clicked=self.play_button.rect.collidepoint(mouse_pos)
        if  button_clicked and not self.stats.game_active:

            # Hide the mouse cursor
            pygame.mouse.set_visible(False)
            # Reset the game statistics

            # self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active= True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining alies and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()




    def _check_keydown_events(self,event):
        """ Respond to key press. """
        if event.key == pygame.K_RIGHT:
            # Move the ship to right.
            # self.ship.rect.x += 1
            self.ship.moving_right = True

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        elif event.key ==  pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self,event):
        """ Respond th key release """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_bullet_alien_collisions(self):
        """ Respond to bullet-alien collisions. """
        # Remoce any bullets and aliens that have collide
        # Check for any bulltes that have hit the alien
        #If so, get rid of the bullet and the alien

        collosions=pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if collosions :
            for alien in collosions.values():
                self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            # Destryoy the existing bullet and create a new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_seed()

            # Increase level
            self.stats.level += 1
            self.sb.prep_level()

    def _fire_bullet(self):
        """ Create new bullet and add it to bullets group. """
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet=Bullet(self)
            self.bullets.add( new_bullet )

    def _update_bullets(self):
        """ Update the position of bullets and get rid of old bullets. """

        #Update bullet positions
        self.bullets.update()

        # Get rid o fbullets that have disapperead
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets))
        self._check_bullet_alien_collisions()




    def _update_aliens(self):
        """ Update the positions of all aliens in the fleet. """
        """ Check if the fleet is at edge then update the position of all aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleeet of aliens """
        # Create an alien and find the number of aliens in a row
        # Spacing between the alien is one alien width

        alien = Alien(self)
        alien_width , alien_height =alien.rect.size
        available_space_x = self.settings.screen_width- (2*alien_width)
        number_aliens_x=available_space_x // (2*alien_width)  # floor division ( // )

        # Determin the number of rows of alien that fit the screen.
        ship_height=self.ship.rect.height
        available_space_y=(self.settings.screen_height - (3*alien_height) - ship_height)
        number_row = available_space_y // (2*alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_row):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number,row_number)






    def _create_alien(self,alien_number,row_number):
        """ Create and alien and place it in the row"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y= alien.rect.height + 2*alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """ Respond apporpriately if any aliens have reached an edge. """
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottom(self):
        """ Check if any alien has reached the bottom of the screen. """
        screen_rect=self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this same as if the ship got hit
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        """ Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        # Update the image on the screen and flip to new screen
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw ths score information
        self.sb.show_score()

        # Draw the paly button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        # Make the most recently drawn screen visible
        pygame.display.flip()

    def _ship_hit(self):
        """ Respond to the ship being hit by an alien """


        if self.stats.ship_left > 0:


            # Decrement the shift left and update the scoreboard.
            self.stats.ship_left -= 1
            self.sb.prep_ships()

            # Get rid of remaining  aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create the new fleet and enter the sip
            self._create_fleet()
            self.ship.center_ship()

            #Pause
            sleep(.5)
        else :

            self.stats.game_active=False
            pygame.mouse.set_visible(True)




"""the if __name__ == '__main__': block is used 
to ensure that specific code within it is only executed when 
the script is run directly, and not when it is imported as a 
module."""

if __name__== '__main__':
    ai=AlienInvasion()
    ai.run_game()
    # Make a game instance, and run the pygame


