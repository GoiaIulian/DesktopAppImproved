from pyglet.gl import *
import ShaderLoader
from ObjLoader import ObjLoader
from pyrr import Vector3, matrix44, Matrix44, quaternion
import time
import numpy
import serial
import pyglet


class Car:
    def __init__(self):

        mesh = ObjLoader()
        mesh.load_model("newCar.obj")

        num_verts = len(mesh.model_vertices) // 3

        self.verts = pyglet.graphics.vertex_list(num_verts, ('v3f', mesh.model_vertices),
                                                            ('t2f', mesh.model_textures),
                                                            ('n3f', mesh.model_normals))

        shader = ShaderLoader.compile_shader("shaders/vert.glsl", "shaders/frag.glsl")

        glUseProgram(shader)

        # vertices
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.verts.vertices)
        glEnableVertexAttribArray(0)
        # textures
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, self.verts.tex_coords)
        glEnableVertexAttribArray(1)
        # normals
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, self.verts.normals)
        glEnableVertexAttribArray(2)

        projection = matrix44.create_perspective_projection_matrix(45.0, 1280 / 720, 0.1, 100.0).flatten().astype("float32")
        view = matrix44.create_from_translation(Vector3([0.0, 0.0, -6.0])).flatten().astype("float32")
        model = matrix44.create_from_translation(Vector3([0.0, 0.0, -1.0])).flatten().astype("float32")

        c_projection = numpy.ctypeslib.as_ctypes(projection)
        c_view = numpy.ctypeslib.as_ctypes(view)
        c_model = numpy.ctypeslib.as_ctypes(model)

        view_loc = glGetUniformLocation(shader, b"view")
        proj_loc = glGetUniformLocation(shader, b"projection")
        model_loc = glGetUniformLocation(shader, b"model")
        self.rotate_loc = glGetUniformLocation(shader, b'rotate')
        self.light_loc = glGetUniformLocation(shader, b"light")

        glUniformMatrix4fv(view_loc, 1, GL_FALSE, c_view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, c_projection)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, c_model)

        # texture settings and loading
        texture = GLuint(0)
        glGenTextures(1, texture)
        glBindTexture(GL_TEXTURE_2D, texture)
        # set the texture wrapping
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set the texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        xmas = pyglet.image.load('car.png')
        image_data = xmas.get_data('RGB', xmas.pitch)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, xmas.width, xmas.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

    def rotate(self, w, i, j, k):
        ct = quaternion.create(i, j, k, w, dtype = "float32")
        rot_y = Matrix44.from_quaternion(ct).flatten().astype("float32")
        c_rotate = numpy.ctypeslib.as_ctypes(rot_y)

        glUniformMatrix4fv(self.rotate_loc, 1, GL_FALSE, c_rotate)
        # glUniformMatrix4fv(self.light_loc, 1, GL_FALSE, c_rotate)


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(400, 300)
        glClearColor(0.2, 0.3, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)

        self.ser = serial.Serial(
            port='COM6',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0xFFFF)


        self.car = Car()

    def on_draw(self):
        self.clear()
        line = self.ser.readline()
        line = line.rstrip(b'\r\n')
        elements = line.decode("utf-8").split(';')
        if elements.__len__() == 5:
            [w, i, k, j, t] = elements
            self.car.rotate(float(w), -float(i), -float(j), float(k))

        self.car.verts.draw(GL_TRIANGLES)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

    def update(self, dt):
        pass

    def on_close(self):
        self.ser.close()
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.set_fullscreen(False)

if __name__ == "__main__":
    window = MyWindow(1280, 720, "Attitude Estimation", resizable=True)
    window.set_fullscreen(True)
    # icon1 = pyglet.image.load('16x16.png')
    # icon2 = pyglet.image.load('32x32.png')
    # window.set_icon(icon1, icon2)
    pyglet.clock.schedule_interval(window.update, 1/60.0)
    pyglet.app.run()