"""
General utility functions and objects.
"""

from math import sqrt


def cube_vertices(x, y, z, n=0.5):
    """
    Creates a list of verticles of a cube.
    @return: The vertices fo a cube aat x, y, z with sidelength 2n
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left:102

        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]

def tex_coord(x, y, n=4):
    """
    Return the bounding vertices of the texture square.
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

def tex_coords(top, bottom, side):
    """
    Return a list of the texture squares for the top, bottom and side.
    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result

def vec_mul(i, c):
    """
    Multiply a vector by a scalar.
    @param i: (tuple) 3d vector to multiply
    @param c: (num) scalar to multiply vector with
    """
    x, y, z = i
    return (x*c, y*c, z*c)

def vec_add(i, j):
    """
    Add two vectors.
    @param i: (tuple) first 3d vector to add
    @param j: (tuple) second 3d vector to add
    @return: sum of the two vectors
    """
    x, y, z = i
    a, b, c = j
    return (x+a, y+b, z+c)

def vec_normalize(i):
    """
    Scale a vector such that its magnitude is 1.
    @param i: (tuple) 3d vector to normalize.
    """
    x, y, z = i
    mag = sqrt(x**2 + y**2 + z**2)
    i_norm = vec_mul(i, 1/mag)
    return i_norm

def vec_ortho(i):
    """
    Create a vector which is orthogonal to a vector.
    @param i: (tuple) 3d vector to use to make the orthogonal vector
    @returns: (tuple) 3d vector on the horizontal plane which points directly to the right of the parameter and is
                      orthogonal to it.

    This function is useful when you have a sight vector and you need a vector which points directly to the right of
    it on the horizontal plane in order to calculate horizontal velocity.
    """
    x, _, z = i
    j = (-z, 0, x) # draw out some examples if you dont believe me ;)
    return j
