"""
Entry point of the program.
This file handles the logisitics of input/output and calls into the World class for the modelling.
"""

from world import World
from config import *

import math
from pyglet.gl import *
from pyglet.window import key, mouse


class Window(pyglet.window.Window):
    """
    Handles the housekeeping, e.g. windowing, resizing, key presses, ...
    """
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.world = World()
        self.mcap = False # mouse capture flag
        self.crosshair = None
        # text that is displayed in the top left of the screen
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18, x=10, y=self.height - 10, anchor_x='left',
                                       anchor_y='top', color=(0, 0, 0, 255))
        # schedules world's update() method to be called TICKS_PER_SEC times per second
        pyglet.clock.schedule_interval(self.world.update, 1.0 / TICKS_PER_SEC)

    def set_mcap(self, mcap):
        """
        Capture or release the mouse.
        @param mcap: If true, mouse is captured, otherwise it is released
        """
        super(Window, self).set_exclusive_mouse(mcap)
        self.mcap = mcap

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when a mouse button is pressed.
        @param x: int of coordinate of the mouse click, always at center if mouse is captured
        @param y: int of coordinate of the mouse click, always at center if mouse is captured
        @param button: int representing mouse button that was cliked, 1=left, 4=right
        @param modifiers: int representing any modifying keys also pressed when mouse clicked
        """
        self.set_mcap(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called when the player moves the mouse.
        @param x: int coordinate of the mouse, always at center if mouse is captured
        @param y: int coordinate of mouse, always at center if mouse is captured
        @param dx: float of x movement of the mouse
        @param dy: float of y movement of the mouse
        """
        if self.mcap:
            self.world.add_player_rotn(dx*SIGHT_SPEED, dy*SIGHT_SPEED)

    def on_key_press(self, symbol, modifiers):
        """
        Called when the player presses a key.
        @param symbol: int representing key pressed
        @param modifiers: int representing modifying keys also pressed
        """
        if symbol == key.W:
            self.world.add_forward_strafe()
        elif symbol == key.S:
            self.world.add_backward_strafe()
        elif symbol == key.A:
            self.world.add_left_strafe()
        elif symbol == key.D:
            self.world.add_right_strafe()
        elif symbol == key.SPACE:
            self.world.add_up_strafe()
        elif symbol == key.F:
            self.world.remove_up_strafe()
        elif symbol == key.ESCAPE:
            self.set_mcap(False)

    def on_key_release(self, symbol, modifiers):
        """
        Called when the player releases a key.
        @param symbol: int corresponding to the key pressed
        @param modifiers: int representing modifying keys also pressed
        """
        # add the opposite strafe to cancel it out
        if symbol == key.W:
            self.world.add_backward_strafe()
        elif symbol == key.S:
            self.world.add_forward_strafe()
        elif symbol == key.A:
            self.world.add_right_strafe()
        elif symbol == key.D:
            self.world.add_left_strafe()
        elif symbol == key.SPACE:
            self.world.remove_up_strafe()
        elif symbol == key.F:
            self.world.add_up_strafe()

    def on_resize(self, width, height):
        """
        Called when the window is resized to a new width and height.
        @width: New window width
        @height: New window height
        """
        self.label.y = height - 10 # resize label
        # resize crosshair
        if self.crosshair:
            self.crosshair.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.crosshair = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """
        Configure opengl to draw in 2d.
        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """
        Configure opengl to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        horiz_rotn, vert_rotn = self.world.get_player_rotn()
        glRotatef(horiz_rotn, 0, 1, 0) # rotate the camera horizontally (around vertical vector)
        sight_vec = self.world.get_player_sight_vec()
        if SIGHT_INVERTED:
            glRotatef(-vert_rotn, sight_vec[2]*-1, 0, sight_vec[0]) # rotate the camera vertically, around the sight vector
        else:
            glRotatef(vert_rotn, sight_vec[2]*-1, 0, sight_vec[0]) # rotate the camera vertically, around the sight vector
        x, y, z = self.world.get_player_posn() # translate the camera to the current player position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.world.draw()
        self.set_2d()
        self.draw_label()
        # draw the crosshair
        glColor3d(0, 0, 0)
        self.crosshair.draw(GL_LINES)

    def draw_label(self):
        """
        Draw the label in the top left of the screen.
        """
        x, y, z = self.world.get_player_posn()
        horiz, vert = self.world.get_player_rotn()
        self.label.text = "fps: %02d, posn: (%.2f, %.2f, %.2f), rotn: (%.2f, %.2f)" % (
            pyglet.clock.get_fps(), x, y, z, horiz, vert)
        self.label.draw()


def setup_opengl():
    glClearColor(0.5, 0.69, 1.0, 1) # color of sky in rgba
    glEnable(GL_CULL_FACE) # enable culling of facets facing away from cam
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    # opengl fog setup
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1)) # set fog color
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def main():
    window = Window(width=800, height=600, caption="voxels", resizable=True)
    window.set_mcap(True)
    setup_opengl()
    pyglet.app.run()


if __name__ == '__main__':
    main()
