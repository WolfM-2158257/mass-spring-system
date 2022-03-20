import random
from tkinter import Tk, Canvas
from graphics_template import *
import math
import time

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
SPRING_REST_LENGTH = 0.75
MASS_COUNT = SPRING_COUNT + 1

FS = 1.0  # force spring
FD = 0.0  # force damping
MASS = 0.09
FG = -9.81  # Gravitational force
# 1 spring: KS = 3 and MASS = 0.075 (set KD=0) correspond to those
# of the experiment in the lab and should result in a period T = +/- 1 sec

mass_cubes = []  # tuple with (mass, pos, pos_prev, fh1, fh2)
springs = []
pos_x = 0


def left_click(event):
    global simulation_done
    simulation_done = True

def apply_forces(i, dt):
    mass, pos, pos_prev, fh1, fh2 = mass_cubes[i].values()
    lenSpring = springs[i-1]["length"]
    mass_cubes[i]["fh1"] = FS*(lenSpring-SPRING_REST_LENGTH)
    acc = mass_cubes[i]["fh1"] / mass
    newPos = (2*pos-pos_prev+(acc+FG)*dt**2)
    mass_cubes[i]["pos_prev"] = pos
    mass_cubes[i]["pos"] = newPos
    springs[i-1]["length"] += pos-newPos

def do_simulation(dt):
    for i, dict in enumerate(mass_cubes[1:]):
        apply_forces(i+1, dt)


def draw_scene():
    # draw_grid (canvas)
    RED = rgb_col(255, 0, 0)
    GREEN = rgb_col(0, 255, 0)
    YELLOW = rgb_col(255, 255, 0)
    draw_line(canvas, w_xmin, FLOOR, w_xmax, FLOOR, RED)
    draw_line(canvas, w_xmin/2, CEILING, w_xmax/2, CEILING, GREEN)
    for i in range(0, SPRING_COUNT):
        pos_y = mass_cubes[i]["pos"]
        length = springs[i]["length"]
        draw_line(canvas, pos_x, pos_y, pos_x, pos_y-length, RED)
    for i in range(0, MASS_COUNT):
        pos_y = mass_cubes[i]["pos"]
        draw_dot(canvas, pos_x, pos_y, YELLOW)


def init_scene():
    totalLength = 0
    for i in range(0, MASS_COUNT):
        length = SPRING_REST_LENGTH + (random.random() - 0.5)
        mass_cube = {"mass": MASS, "pos": CEILING - totalLength,
                     "pos_prev": CEILING - totalLength, "fh1": 0, "fh2": 0}
        mass_cubes.append(mass_cube)
        spring = {"length": length}
        springs.append(spring)
        totalLength += length
    springs.pop()
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
