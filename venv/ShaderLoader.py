import ctypes
from pyglet.gl import *


def load_shader(shader_file):
    with open(shader_file) as f:
        shader_source = f.read()
    return str.encode(shader_source)


def compile_shader(vs, fs):
    vert_shader = load_shader(vs)
    frag_shader = load_shader(fs)

    vertex_buff = ctypes.create_string_buffer(vert_shader)
    c_vertex = ctypes.cast(ctypes.pointer(ctypes.pointer(vertex_buff)), ctypes.POINTER(ctypes.POINTER(GLchar)))
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, 1, c_vertex, None)
    glCompileShader(vertex_shader)

    fragment_buff = ctypes.create_string_buffer(frag_shader)
    c_fragment = ctypes.cast(ctypes.pointer(ctypes.pointer(fragment_buff)), ctypes.POINTER(ctypes.POINTER(GLchar)))
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, 1, c_fragment, None)
    glCompileShader(fragment_shader)

    shader = glCreateProgram()
    glAttachShader(shader, vertex_shader)
    glAttachShader(shader, fragment_shader)
    glLinkProgram(shader)

    return shader