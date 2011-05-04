"""Simple functions for coordinate conversion."""
__author__="Micah"
__date__ ="$Mar 20, 2011 8:58:14 PM$"

import math

def spherical(x, y, z):
    """Return (rho, theta, phi) based on Cartesian coordinates."""
    # distance from origin
    rho = distance(x, y, z)
    # inclination
    theta = math.acos(z / rho)
    # azimuth (rotation about z-axis)
    phi = math.atan2(y, x)
    return [rho, theta, phi]

def cartesian(rho, theta, phi):
    """Return (x, y, z) based on spherical coordinates."""
    x = rho * math.sin(theta) * math.cos(phi)
    y = rho * math.sin(theta) * math.sin(phi)
    z = rho * math.cos(theta)
    return [x, y, z]

def distance(x, y, z):
    """Return the distance from the specified Cartesian point to the origin."""
    return math.sqrt(x**2 + y**2 + z**2)

def magnitude(vector):
    """Return the magnitude of the specified vector."""
    return math.sqrt(sum(component**2 for component in vector))

def normalize(vector):
    """Return the unit vector."""
    return [component / magnitude(vector) for component in vector]