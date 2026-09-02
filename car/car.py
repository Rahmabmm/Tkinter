import pygame
from pygame.locals import *
import random

pygame.init()

# Create the window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Car Game")

# Colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# Game settings
gameover = False
speed = 2
score = 0

# Markers size
marker_width = 10
marker_height = 50

# Road and edge markers
road = (100, 0, 300, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# X coordinates of lanes
left_lane = 150
center_lane = 250
right_lane = 350

lanes = [left_lane, center_lane, right_lane]

# For animating movement of the lane markers
lane_marker_move_y = 0


class Vehicle(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Scale the image so it fits in the lane
        image_scale = 45 / image.get_rect().width

        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)

        self.image = pygame.transform.scale(
            image,
            (new_width, new_height)
        )

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):

    def __init__(self, x, y):
        image = pygame.image.load("car/images/car.png")
        super().__init__(image, x, y)


# Player's starting coordinates
player_x = 250
player_y = 400

# Create the player's car
player_group = pygame.sprite.Group()

player = PlayerVehicle(
    player_x,
    player_y
)

player_group.add(player)


# Load the other vehicle images
image_filenames = [
    "pickup_truck.png",
    "semi_trailer.png",
    "taxi.png",
    "van.png"
]

vehicle_images = []

for image_filename in image_filenames:
    image = pygame.image.load(
        "car/images/" + image_filename
    )

    vehicle_images.append(image)


# Sprite group for other vehicles
vehicle_group = pygame.sprite.Group()


# Load the crash image
crash = pygame.image.load(
    "car/images/crash.png"
)

crash_rect = crash.get_rect()


# Game loop
clock = pygame.time.Clock()

fps = 120

running = True

while running:

    clock.tick(fps)

    # Events
    for event in pygame.event.get():

        if event.type == QUIT:
            running = False

        # Move player's car
        if event.type == KEYDOWN and not gameover:

            # Move left
            if event.key == K_LEFT and player.rect.centerx > left_lane:

                player.rect.centerx -= 100

            # Move right
            elif event.key == K_RIGHT and player.rect.centerx < right_lane:

                player.rect.centerx += 100

    # Only run the game if the player has not crashed
    if not gameover:

        # Check if there is a side swipe collision
        for vehicle in vehicle_group:

            if pygame.sprite.collide_rect(player, vehicle):

                gameover = True

                crash_rect.center = [
                    player.rect.centerx,
                    player.rect.top
                ]

        # Draw the grass
        screen.fill(green)

        # Draw the road
        pygame.draw.rect(
            screen,
            gray,
            road
        )

        # Draw the edge markers
        pygame.draw.rect(
            screen,
            yellow,
            left_edge_marker
        )

        pygame.draw.rect(
            screen,
            yellow,
            right_edge_marker
        )

        # Draw the lane markers
        lane_marker_move_y += speed * 2

        if lane_marker_move_y >= marker_height * 2:
            lane_marker_move_y = 0

        for y in range(
            marker_height * -2,
            height,
            marker_height * 2
        ):

            pygame.draw.rect(
                screen,
                white,
                (
                    left_lane + 45,
                    y + lane_marker_move_y,
                    marker_width,
                    marker_height
                )
            )

            pygame.draw.rect(
                screen,
                white,
                (
                    center_lane + 45,
                    y + lane_marker_move_y,
                    marker_width,
                    marker_height
                )
            )

        # Add up to two vehicles
        if len(vehicle_group) < 2:

            # Make sure there is enough space between vehicles
            add_vehicle = True

            for vehicle in vehicle_group:

                if vehicle.rect.top < vehicle.rect.height * 1.5:

                    add_vehicle = False

            if add_vehicle:

                # Select a random lane
                lane = random.choice(lanes)

                # Select a random vehicle image
                image = random.choice(vehicle_images)

                # Create the vehicle
                vehicle = Vehicle(
                    image,
                    lane,
                    -height / 2
                )

                vehicle_group.add(vehicle)

        # Move the other vehicles
        for vehicle in vehicle_group:

            vehicle.rect.y += speed

            # Remove vehicle when it leaves the screen
            if vehicle.rect.top >= height:

                vehicle.kill()

                # Increase score
                score += 1

                # Increase speed every 5 vehicles
                if score > 0 and score % 5 == 0:

                    speed += 1

        # Check for head-on collision
        if pygame.sprite.spritecollide(
            player,
            vehicle_group,
            False
        ):

            gameover = True

            crash_rect.center = [
                player.rect.centerx,
                player.rect.top
            ]

        # Draw the other vehicles
        vehicle_group.draw(screen)

        # Draw the player's car
        player_group.draw(screen)

        # Display the score
        font = pygame.font.Font(
            pygame.font.get_default_font(),
            16
        )

        text = font.render(
            "Score: " + str(score),
            True,
            white
        )

        text_rect = text.get_rect()

        text_rect.center = (50, 450)

        screen.blit(
            text,
            text_rect
        )

    # Display game over screen
    if gameover:

        screen.blit(
            crash,
            crash_rect
        )

        pygame.draw.rect(
            screen,
            red,
            (0, 50, width, 100)
        )

        font = pygame.font.Font(
            pygame.font.get_default_font(),
            16
        )

        text = font.render(
            "Game Over! Press Y to play again or N to quit",
            True,
            white
        )

        text_rect = text.get_rect()

        text_rect.center = (
            width / 2,
            100
        )

        screen.blit(
            text,
            text_rect
        )

        # Check for restart or quit
        for event in pygame.event.get():

            if event.type == KEYDOWN:

                if event.key == K_y:

                    # Reset the game
                    gameover = False
                    speed = 2
                    score = 0

                    player.rect.center = [
                        center_lane,
                        player_y
                    ]

                    vehicle_group.empty()

                elif event.key == K_n:

                    running = False

    # Update the screen
    pygame.display.update()


pygame.quit()