import random
from tkinter import Tk, Canvas
from graphics_template import *
import math
import time
import copy

vp_width, vp_height = 1024, 768
w_xmin, w_ymin, w_xmax = -10, 0, 10
w_ymax = w_ymin + (w_xmax - w_xmin)/vp_width * vp_height

simulation_done = False
DELTA_TSIM = 0.0005
DELTA_TDRAW = 0.02  # 50 fps

CEILING = w_ymax - 0.5
FLOOR = w_ymin + 0.5

# variables
SPRING_COUNT = 10
SPRING_REST_LENGTH = 0.9
MASS_COUNT = SPRING_COUNT + 1

FS = 10.0  # force spring
FD = 0.5  # force damping
MASS = 0.09
AG = -9.81  # Gravitational force
# 1 spring: KS = 3 and MASS = 0.075 (set KD=0) correspond to those
# of the experiment in the lab and should result in a period T = +/- 1 sec

old_mass_cubes = []  # dict with (mass, pos, pos_prev, fh1, fh2)
old_springs = []  # (length, length_prev)
new_springs = []
new_mass_cubes = []
pos_x = 0


def left_click(event):
    global simulation_done
    simulation_done = True


def change_cube_pos(i, newPos):
    new_mass_cubes[i]["pos_prev"] = old_mass_cubes[i]["pos"]
    new_mass_cubes[i]["pos"] = newPos


def change_spring_length(i, newLength):
    new_springs[i]["length_prev"] = old_springs[i]["length"]
    new_springs[i]["length"] = newLength


def calc_damping_v(dt, lenSpringNext, i):
    lenSpringPrev = old_springs[i]["length_prev"]
    y1 = lenSpringPrev - SPRING_REST_LENGTH
    y2 = lenSpringNext - SPRING_REST_LENGTH
    v = (y2 - y1) / (2*dt)
    return v


def apply_forces(i, dt):
    mass, pos, pos_prev, fh1, fh2, fd1, fd2  = old_mass_cubes[i].values()

    ah1 = 0
    if i >= 1:
        lenSpringAbove = old_springs[i-1]["length"]
        new_mass_cubes[i]["fh1"] = FS*(lenSpringAbove - SPRING_REST_LENGTH)
        ah1 = old_mass_cubes[i]["fh1"] / mass
    ah2 = 0
    if i < SPRING_COUNT:
        lenSpringUnder = old_springs[i]["length"]
        new_mass_cubes[i]["fh2"] = -FS*(lenSpringUnder - SPRING_REST_LENGTH)
        ah2 = old_mass_cubes[i]["fh2"] / mass

    ad1 = fd1 / mass
    ad2 = fd2 / mass
    newPos = (2*pos - pos_prev + (ah1+ah2+ad1+ad2+AG) * dt**2)


    change_cube_pos(i, newPos)
    if i >= 1:
        newLength = old_springs[i-1]["length"] + (pos - newPos)
        v = calc_damping_v(dt, newLength, i - 1)
        new_mass_cubes[i]["fd1"] = FD*v
        change_spring_length(i-1, newLength)
    if i < SPRING_COUNT:
        newLength = old_springs[i]["length"] - (pos - newPos)
        v = calc_damping_v(dt, newLength, i)
        new_mass_cubes[i]["fd2"] = -FD*v
        change_spring_length(i, newLength)


def do_simulation(dt):
    for i in range(1, len(old_mass_cubes)):
        apply_forces(i, dt)


def draw_scene():
    global new_mass_cubes
    global new_springs
    # draw_grid (canvas)
    RED = rgb_col(255, 0, 0)
    GREEN = rgb_col(0, 255, 0)
    YELLOW = rgb_col(255, 255, 0)
    draw_line(canvas, w_xmin, FLOOR, w_xmax, FLOOR, RED)
    draw_line(canvas, w_xmin/2, CEILING, w_xmax/2, CEILING, GREEN)
    for i in range(0, SPRING_COUNT):
        pos_y = new_mass_cubes[i]["pos"]
        length = new_springs[i]["length"]
        draw_line(canvas, pos_x, pos_y, pos_x, pos_y-length, RED)
    for i in range(0, MASS_COUNT):
        pos_y = new_mass_cubes[i]["pos"]
        draw_dot(canvas, pos_x, pos_y, YELLOW)
    new_springs = copy.copy(old_springs)
    new_mass_cubes = copy.copy(old_mass_cubes)



def init_scene():
    totalLength = 0
    for i in range(0, MASS_COUNT):
        length = SPRING_REST_LENGTH + (random.random() - 0.5)
        mass_cube = {"mass": MASS, "pos": CEILING - totalLength,
                     "pos_prev": CEILING - totalLength, "fh1": 0, "fh2": 0, "fd1": 0, "fd2": 0}
        old_mass_cubes.append(mass_cube)
        spring = {"length": length, "length_prev": length}
        old_springs.append(spring)
        totalLength += length
    old_springs.pop()
    global new_springs
    new_springs = copy.copy(old_springs)
    global new_mass_cubes
    new_mass_cubes = copy.copy(old_mass_cubes)
    draw_scene()


window = Tk()
canvas = Canvas(window, width=vp_width, height=vp_height, bg=rgb_col(0, 0, 0))
canvas.pack()
canvas.bind("<Button-1>", left_click)

init_graphics(vp_width, vp_height, w_xmin, w_ymin, w_xmax)


# time.perf_counter() -> float. Return the value (in fractional seconds)
# of a performance counter, i.e. a clock with the highest available resolution
# to measure a short duration. It does include time elapsed during sleep and
# is system-wide. The reference point of the returned value is undefined,
# so that only the difference between the results of consecutive calls is valid.

init_time = time.perf_counter()
prev_draw_time = 0
prev_sim_time = 0

init_scene()

while (not simulation_done):
    # simulating
    sim_dt = time.perf_counter() - init_time - prev_sim_time
    if (sim_dt > DELTA_TSIM):
        do_simulation(DELTA_TSIM)
        prev_sim_time += DELTA_TSIM
    # drawing
    draw_dt = time.perf_counter() - init_time - prev_draw_time
    if (draw_dt > DELTA_TDRAW):  # 50 fps
        canvas.delete("all")
        draw_scene()
        canvas.update()
        prev_draw_time += DELTA_TDRAW
