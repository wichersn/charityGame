import math

#arguments: (magnatude, angle)
def polar_to_cart(polarChords):
    r, theta = polarChords
    return r * math.cos(theta), r * math.sin(theta)

#returns (magnatude, angle)
def cart_to_polar(cartChords):
    x, y = cartChords
    angle = -math.atan2(x, y) + math.pi/2

    return math.sqrt(float(x*x + y*y)), angle
