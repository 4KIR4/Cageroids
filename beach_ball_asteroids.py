import sys
import pygame
import math
import random

###############################################################################
##  Main Logic Start
pygame.init()

##  The Screen
size = width, height = 640, 480
screen = pygame.display.set_mode(size)
black = pygame.Color(0, 0, 0, 0)
white = pygame.Color(255, 255, 255, 255)
myfont = pygame.font.SysFont("Arial", 16)
bigfont = pygame.font.SysFont("Arial", 66)

###############################################################################
class game_object(pygame.sprite.Sprite):
	rotation = 0.0
	radius = 0.0
	can_loop = True

	def __init__(self, imageFileName, canLoop):
		self.image = pygame.image.load(imageFileName)
		self.rect = self.image.get_rect()

		if (self.rect.width > self.rect.height):
			self.radius = self.rect.width / 2.0

		else:
			self.radius = self.rect.height / 2.0

		self.can_loop = canLoop
		self.location = [0.0, 0.0]
		self.velocity = [0.0, 0.0]
		self.center = [self.location[0] + self.rect.width / 2.0, self.location[1] + self.rect.height / 2.0]
	
	def Move(self):
		self.location[0] = self.location[0] + self.velocity[0]
		self.location[1] = self.location[1] + self.velocity[1]
		self.center[0] = self.location[0] + self.rect.width / 2.0
		self.center[1] = self.location[1] + self.rect.height / 2.0

		if (self.can_loop):
			if self.location[0] < 0:
				self.location[0] = width
			
			elif self.location[0] > width:
				self.location[0] = 0
			
			if self.location[1] < 0:
				self.location[1] = height
	
			elif self.location[1] > height:
				self.location[1] = 0
				
	def DrawRotatedSprite(self, targetSurface, rotation):
		##  Refresh the image, or it will be irreversibly degraded by the rotation
		new_image = pygame.transform.rotate(self.image, rotation)
		rotated_rect = new_image.get_rect()
		clipped_rect = pygame.Rect(
			(self.rect.width - rotated_rect.width) / 2,
			(self.rect.height - rotated_rect.height) / 2,
			self.rect.width,
			self.rect.height)
		image_rect = clipped_rect.copy()
		image_rect = image_rect.move(self.location)
		targetSurface.blit(new_image, image_rect)

		##  Draw a second image if this image is going over the edge
		if (self.can_loop):
			draw_second_image = False
			##  Copy the second_image_location, because if I set second_image_location = location,
			##  Any changes to second_image_location will also apply to location!
			second_image_location = [self.location[0], self.location[1]]
			second_image_rect = clipped_rect.copy()
			if (self.location[0] > width - self.rect.width):
				draw_second_image = True
				second_image_location[0] = self.location[0] - width
			if (self.location[1] > height - self.rect.height):
				draw_second_image = True
				second_image_location[1] = self.location[1] - height
			if (draw_second_image):
				second_image_rect = second_image_rect.move(second_image_location)
				targetSurface.blit(new_image, second_image_rect)

	def CheckCollision(self, someOtherGameObject):
		##  Check for collision
		collided = False

		vectorFromSelfToObject = [0.0, 0.0]
		vectorFromSelfToObject[0] = someOtherGameObject.center[0] - self.center[0]
		vectorFromSelfToObject[1] = someOtherGameObject.center[1] - self.center[1]

		distanceToObject = math.sqrt(vectorFromSelfToObject[0] ** 2 + vectorFromSelfToObject[1] ** 2)

		collided = distanceToObject < self.radius + someOtherGameObject.radius

		##  Check for collision with my center on the opposite side of
		##  The screen if this image is going over the edge
		if (not collided and self.can_loop):
			second_image_location = [self.location[0], self.location[1]]
			check_second_image = False
			if (self.location[0] > width - self.rect.width):
				second_image_location[0] = self.location[0] - width
				check_second_image = True
			if (self.location[1] > height - self.rect.height):
				second_image_location[1] = self.location[1] - height
				check_second_image = True

			if (check_second_image is True):
				second_image_center = [0.0, 0.0]
				second_image_center[0] = second_image_location[0] + self.rect.width / 2
				second_image_center[1] = second_image_location[1] + self.rect.height / 2

				vectorFromSecondToObject = [0.0, 0.0]
				vectorFromSecondToObject[0] = someOtherGameObject.center[0] - second_image_center[0]
				vectorFromSecondToObject[1] = someOtherGameObject.center[1] - second_image_center[1]

				distanceToSecond = math.sqrt(vectorFromSecondToObject[0] ** 2 + vectorFromSecondToObject[1] ** 2)

				collided = distanceToSecond < self.radius + someOtherGameObject.radius
				
			
		return collided

###############################################################################
class ship(game_object):
	rotation = 0.0
	image = pygame.image.load("emmy.png")

	def __init__(self, imageFileName, canLoop, newLocation):
		super().__init__(imageFileName, canLoop)
		self.location = [newLocation[0], newLocation[1]]
		self.location[1] = newLocation[1]

	def GetUserInput(self):
		key = pygame.key.get_pressed()

		##  Calculate the player's ship's rotation and velocity
		if (key[pygame.K_LEFT]):
			self.rotation = self.rotation + 5

		if (key[pygame.K_RIGHT]):
			self.rotation = self.rotation - 5

		if (key[pygame.K_UP]):
			linearAcceleration = 1
		elif (key[pygame.K_DOWN]):
			linearAcceleration = -0.5
		else:
			linearAcceleration = 0
			
		accelerationVector = [0.0, 0.0]
		rotationInRadians = math.radians(self.rotation)
		accelerationVector[0] = linearAcceleration * math.cos(rotationInRadians)
		accelerationVector[1] = -linearAcceleration * math.sin(rotationInRadians)

		##  Add the acceleration vector to the velocity vector
		self.velocity[0] += accelerationVector[0]
		self.velocity[1] += accelerationVector[1]

		if (key[pygame.K_SPACE] and aBullet.ready_to_spawn):
			##  Give the bullet a new location
			spawnLocation = self.center

			##  Spawn the bullet with a launch speed of 25
			spawnVelocity = [0, 0]
			spawnVelocity[0] = 25.0 * math.cos(rotationInRadians)
			spawnVelocity[1] = -25.0 * math.sin(rotationInRadians)
			spawnVelocity[0] += self.velocity[0]
			spawnVelocity[1] += self.velocity[1]

			aBullet.Spawn(spawnLocation, spawnVelocity)
		

	def Move(self):
		##  ToDo: Limit the ship's speed to 5
		speed = math.sqrt( self.velocity[0] ** 2 + self.velocity[1] ** 2 )
		if (speed > 5.0):
			##  Build a vector in the direction of our velocity, but with a magnitude of 1
			velNormalized = [0.0, 0.0]
			velNormalized[0] = self.velocity[0] / speed
			velNormalized[1] = self.velocity[1] / speed

			##  Use that vector to limit our ship's speed to 5
			self.velocity[0] = 5.0 * velNormalized[0]
			self.velocity[1] = 5.0 * velNormalized[1]
		
		super().Move()

	def Reset(self):
		self.location[0] = 300.0
		self.location[1] = 200.0
		self.velocity[0] = 0.0
		self.velocity[1] = 0.0

###############################################################################
class bullet(game_object):
	image = pygame.image.load("attack.gif")
	rect = image.get_rect()
	rotation = 0.0
	ready_to_spawn = True

	def __init__(self, imageFileName, initPosition, initVelocity):
		super().__init__(imageFileName, False)
		
		self.location = [initPosition[0], initPosition[1]]
		self.velocity = [initVelocity[0], initVelocity[1]]
		self.ready_to_spawn = True
		
	def Spawn(self, initPosition, initVelocity):
		self.location = [initPosition[0], initPosition[1]]
		self.velocity = [initVelocity[0], initVelocity[1]]
		self.ready_to_spawn = False

	def Reset(self):
		self.location[0] = -1000.0
		self.location[1] = -1000.0
		self.velocity[0] = 0.0
		self.velocity[1] = 0.0
		self.ready_to_spawn = True
		
	def Move(self):
		super().Move()
		if self.location[0] < 0:
			self.Reset()
					
		elif self.location[0] > width:
			self.Reset()
					
		if self.location[1] < 0:
			self.Reset()
			
		elif self.location[1] > height:
			self.Reset()
	
###############################################################################
class asteroid(game_object):
	image = pygame.image.load("nick.png")
	rect = image.get_rect()
	rotation = 0.0
	angular_velocity = 0.0

	def __init__(self, imageFileName, canLoop):
		super().__init__(imageFileName, canLoop)
		self.Reset()

	def Move(self):
		self.rotation = self.rotation + self.angular_velocity
		super().Move()

	def Reset(self):
		self.location = [random.randint(0, screen.get_width()), random.randint(0, screen.get_height())]
		self.velocity = [random.randint(-3, 3), random.randint(-3, 3)]
		self.angular_velocity = random.randint(1, 3)
		self.rect = self.image.get_rect()
		self.center[0] = self.location[0] + self.rect.width / 2.0
		self.center[1] = self.location[1] + self.rect.height / 2.0


###############################################################################
## Sprite creation
theShip = ship("emmy.png", True, [300.0, 200.0])
aBullet = bullet("attack.gif", (-10.0, -10.0), (0.0, 0.0))
asteroid1 = asteroid("nick.png", True )
asteroid2 = asteroid("nick.png", True )
asteroid3 = asteroid("nick.png", True )

asteroids = (asteroid1, asteroid2, asteroid3)

#player = pygame.sprite.Group()
#asteroids = pygame.sprite.Group()

#player.add(theShip, aBullet)
#asteroids.add(asteroid1, asteroid2, asteroid3)

#for anAsteroid in asteroids:
#    print("Vecloty = ", anAsteroid.velocity);
asteroid2.rotation = 69.0
#print("asteroid1.rotation = ", asteroid1.rotation)
#print("asteroid2.rotation = ", asteroid2.rotation)

keepGoing = True
playerIsAlive = True
clock = pygame.time.Clock()
score = 0
lives = 3

while keepGoing:
	clock.tick(30)
	
	eventList = pygame.event.get()
	for event in eventList:
		if event.type == pygame.QUIT:
			keepGoing = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				keepGoing = False
			elif event.key == pygame.K_RETURN and not playerIsAlive:
				playerIsAlive = True
				lives = 3
				score = 0
				for anAsteroid in asteroids:
					anAsteroid.Reset()

	for anAsteroid in asteroids:
		anAsteroid.Move()

	if playerIsAlive:
		theShip.GetUserInput()

		theShip.Move()

		for anAsteroid in asteroids:
			collided_with_ship = False
			collided_with_ship = anAsteroid.CheckCollision(theShip)
			collided_with_bullet = False
			collided_with_bullet = anAsteroid.CheckCollision(aBullet)

			if (collided_with_ship):
				print("Player is DEAD!")
				score = score - 100
				lives = lives - 1
				theShip.Reset()

				for anAsteroid in asteroids:
					while anAsteroid.CheckCollision(theShip):
						print( "Collided... reseting asteroid" )
						anAsteroid.Reset()
			
				# Do logic for re-spawning the player at center
				# IF it is clear of Asteroids
			if (collided_with_bullet):
				score = score + 1000
				anAsteroid.Reset()
				aBullet.Reset()
		

	## Setting background to blue
	screen.fill(black)

	theShip.DrawRotatedSprite(screen, theShip.rotation)
	
	for anAsteroid in asteroids:
		anAsteroid.DrawRotatedSprite(screen, anAsteroid.rotation)

	aBullet.Move()
	aBullet.DrawRotatedSprite(screen, aBullet.rotation)
	## Printing Score and Lives to the game window
	scoretext = myfont.render("Score: {0}".format(score), 1, white)
	screen.blit(scoretext, (5, 10))

	lifetext = myfont.render("Lives: {}".format(lives), 1, white)
	screen.blit(lifetext, (5, 30))
	
	if lives <= 0:
		gameover = bigfont.render("YOU GOT CAGED!", 1, white)
		gamecontinue = myfont.render("Press Enter to continue", 1, white)
		screen.blit(gameover, [40, 100])
		screen.blit(gamecontinue, [240, 400])
		playerIsAlive = False


	pygame.display.flip()

#exit cleanly
pygame.quit()
sys.exit()
