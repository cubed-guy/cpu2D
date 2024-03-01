# DONE: Draw to cells
# DONE: Generate Groups
# DONE: Update Group Values
# DONE: Update Transistor States
# DONE: Resistors are not insulators
# DONE: Copy-paste support
# DONE: Overlap Support
# TODO: Optimise Resistor Updates
# TODO: Optimise matrix rendering
# TODO: Rewind

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

from enum import Enum, auto

import cpu
import pygame
from pygame.locals import *
pygame.font.init()
font  = pygame.font.Font('../Product Sans Regular.ttf', 16)
sfont = pygame.font.Font('../Product Sans Regular.ttf', 12)

c = type('c', (), {'__matmul__': (lambda s, x: (*x.to_bytes(3, 'big'),)), '__sub__': (lambda s, x: (x&255,)*3)})()
bg = c-34
fg = c@0xff9088
green = c@0xa0ffe0

fps = 60

ZOOM_FAC_NUM = 4
ZOOM_FAC_DEN = 5

w, h = res = (1280, 800)

def updateStat(msg = None, update = True):
	# call this if you have a long loop that'll taking too long
	rect = (0, h-20, w, 21)
	display.fill(c-0, rect)

	mouse_pos = pygame.mouse.get_pos()
	cell = from_screen_space(mouse_pos, view_rect, size)
	tsurf = sfont.render(msg or f'{cell} {paint_mode} {type(selected_group)} {copy_region} {copy_mode}', True, c--1)
	display.blit(tsurf, (5, h-20))

	if update: pygame.display.update(rect)

def resize(size):
	global w, h, res, display
	w, h = res = size
	view_rect.size = size
	display = pygame.display.set_mode(res, RESIZABLE)
	updateDisplay()

def updateDisplay():
	display.fill(bg)

	if copy_mode in (CopyMode.select, CopyMode.ready):
		surf = circuit.render(size, view_rect, selected_group, selected_region=copy_region)
	else:
		surf = circuit.render(size, view_rect, selected_group)
	display.blit(surf, (0, 0))

	updateStat(update = False)
	pygame.display.flip()

def toggleFullscreen():
	global pres, res, w, h, display
	res, pres =  pres, res
	w, h = res
	if display.get_flags()&FULLSCREEN: resize(res)
	else:
		view_rect.size = res
		display = pygame.display.set_mode(res, FULLSCREEN)
		updateDisplay()

def from_screen_space(screen_pos, ref_rect, ref_size):
	x = screen_pos[0] + ref_rect.left
	y = screen_pos[1] + ref_rect.top

	return x // size, y // size

class CopyMode(Enum):
	inactive = auto()
	active = auto()
	select = auto()
	ready = auto()

view_rect = pygame.Rect(440, 220, w, h)
dragging = False
ticks = 0

selected_group = None
size = 64
paint_mode = cpu.Cell.conductor
circuit = cpu.Circuit(500, 500)

# circuit.mat[4][12] = cpu.Cell.live
# circuit.mat[4][20] = cpu.Cell.ground
# circuit.mat[5][12] = cpu.Cell.conductor
# circuit.mat[5][20] = cpu.Cell.conductor
# circuit.mat[6][12] = cpu.Cell.conductor
# circuit.mat[6][18] = cpu.Cell.ground
# circuit.mat[6][20] = cpu.Cell.conductor
# circuit.mat[7][10] = cpu.Cell.ground
# circuit.mat[7][12] = cpu.Cell.transistor_gate
# circuit.mat[7][18] = cpu.Cell.conductor
# circuit.mat[7][20] = cpu.Cell.transistor_gate
# circuit.mat[8][10] = cpu.Cell.resistor
# circuit.mat[8][11] = cpu.Cell.conductor
# circuit.mat[8][12] = cpu.Cell.transistor
# circuit.mat[8][13] = cpu.Cell.conductor
# circuit.mat[8][18] = cpu.Cell.resistor
# circuit.mat[8][19] = cpu.Cell.conductor
# circuit.mat[8][20] = cpu.Cell.transistor
# circuit.mat[8][21] = cpu.Cell.conductor
# circuit.mat[9][11] = cpu.Cell.transistor_gate
# circuit.mat[9][13] = cpu.Cell.transistor
# circuit.mat[9][14] = cpu.Cell.live
# circuit.mat[9][19] = cpu.Cell.transistor_gate
# circuit.mat[9][21] = cpu.Cell.transistor
# circuit.mat[9][22] = cpu.Cell.conductor
# circuit.mat[9][23] = cpu.Cell.live
# circuit.mat[10][10] = cpu.Cell.live
# circuit.mat[10][11] = cpu.Cell.transistor
# circuit.mat[10][12] = cpu.Cell.conductor
# circuit.mat[10][13] = cpu.Cell.transistor_gate
# circuit.mat[10][17] = cpu.Cell.live
# circuit.mat[10][18] = cpu.Cell.conductor
# circuit.mat[10][19] = cpu.Cell.transistor
# circuit.mat[10][20] = cpu.Cell.conductor
# circuit.mat[10][21] = cpu.Cell.transistor_gate
# circuit.mat[11][11] = cpu.Cell.transistor_gate
# circuit.mat[11][13] = cpu.Cell.resistor
# circuit.mat[11][14] = cpu.Cell.ground
# circuit.mat[11][19] = cpu.Cell.transistor_gate
# circuit.mat[11][21] = cpu.Cell.resistor
# circuit.mat[11][22] = cpu.Cell.conductor
# circuit.mat[11][23] = cpu.Cell.ground
# circuit.mat[12][11] = cpu.Cell.conductor
# circuit.mat[12][19] = cpu.Cell.conductor
# circuit.mat[13][11] = cpu.Cell.conductor
# circuit.mat[13][19] = cpu.Cell.conductor
# circuit.mat[14][11] = cpu.Cell.ground
# circuit.mat[14][19] = cpu.Cell.live

circuit.mat[2][4] = cpu.Cell.live
circuit.mat[2][5] = cpu.Cell.conductor
circuit.mat[2][6] = cpu.Cell.conductor
circuit.mat[2][7] = cpu.Cell.conductor
circuit.mat[2][8] = cpu.Cell.conductor
circuit.mat[2][9] = cpu.Cell.conductor
circuit.mat[2][10] = cpu.Cell.conductor
circuit.mat[2][11] = cpu.Cell.conductor
circuit.mat[2][12] = cpu.Cell.conductor
circuit.mat[2][13] = cpu.Cell.conductor
circuit.mat[2][14] = cpu.Cell.conductor
circuit.mat[2][15] = cpu.Cell.conductor
circuit.mat[2][16] = cpu.Cell.conductor
circuit.mat[2][22] = cpu.Cell.conductor
circuit.mat[3][16] = cpu.Cell.conductor
circuit.mat[3][22] = cpu.Cell.conductor
circuit.mat[4][16] = cpu.Cell.conductor
circuit.mat[4][22] = cpu.Cell.conductor
circuit.mat[5][4] = cpu.Cell.ground
circuit.mat[5][5] = cpu.Cell.conductor
circuit.mat[5][6] = cpu.Cell.conductor
circuit.mat[5][7] = cpu.Cell.conductor
circuit.mat[5][8] = cpu.Cell.conductor
circuit.mat[5][9] = cpu.Cell.conductor
circuit.mat[5][14] = cpu.Cell.conductor
circuit.mat[5][15] = cpu.Cell.conductor
circuit.mat[5][16] = cpu.Cell.conductor
circuit.mat[5][22] = cpu.Cell.conductor
circuit.mat[6][9] = cpu.Cell.conductor
circuit.mat[6][14] = cpu.Cell.conductor
circuit.mat[6][16] = cpu.Cell.transistor_gate
circuit.mat[6][22] = cpu.Cell.conductor
circuit.mat[7][9] = cpu.Cell.conductor
circuit.mat[7][11] = cpu.Cell.ground
circuit.mat[7][12] = cpu.Cell.conductor
circuit.mat[7][13] = cpu.Cell.conductor
circuit.mat[7][14] = cpu.Cell.overlap
circuit.mat[7][15] = cpu.Cell.conductor
circuit.mat[7][16] = cpu.Cell.transistor
circuit.mat[7][22] = cpu.Cell.conductor
circuit.mat[8][9] = cpu.Cell.conductor
circuit.mat[8][14] = cpu.Cell.conductor
circuit.mat[8][16] = cpu.Cell.conductor
circuit.mat[8][17] = cpu.Cell.resistor
circuit.mat[8][18] = cpu.Cell.conductor
circuit.mat[8][19] = cpu.Cell.live
circuit.mat[8][22] = cpu.Cell.conductor
circuit.mat[9][9] = cpu.Cell.conductor
circuit.mat[9][14] = cpu.Cell.conductor
circuit.mat[9][16] = cpu.Cell.conductor
circuit.mat[9][22] = cpu.Cell.conductor
circuit.mat[10][9] = cpu.Cell.conductor
circuit.mat[10][14] = cpu.Cell.conductor
circuit.mat[10][16] = cpu.Cell.conductor
circuit.mat[10][22] = cpu.Cell.conductor
circuit.mat[11][9] = cpu.Cell.conductor
circuit.mat[11][14] = cpu.Cell.conductor
circuit.mat[11][16] = cpu.Cell.conductor
circuit.mat[11][22] = cpu.Cell.conductor
circuit.mat[12][9] = cpu.Cell.conductor
circuit.mat[12][14] = cpu.Cell.conductor
circuit.mat[12][16] = cpu.Cell.conductor
circuit.mat[12][22] = cpu.Cell.conductor
circuit.mat[13][7] = cpu.Cell.conductor
circuit.mat[13][8] = cpu.Cell.conductor
circuit.mat[13][9] = cpu.Cell.conductor
circuit.mat[13][14] = cpu.Cell.conductor
circuit.mat[13][16] = cpu.Cell.conductor
circuit.mat[13][22] = cpu.Cell.conductor
circuit.mat[14][7] = cpu.Cell.conductor
circuit.mat[14][9] = cpu.Cell.transistor_gate
circuit.mat[14][14] = cpu.Cell.conductor
circuit.mat[14][16] = cpu.Cell.conductor
circuit.mat[14][22] = cpu.Cell.conductor
circuit.mat[15][4] = cpu.Cell.ground
circuit.mat[15][5] = cpu.Cell.conductor
circuit.mat[15][6] = cpu.Cell.conductor
circuit.mat[15][7] = cpu.Cell.overlap
circuit.mat[15][8] = cpu.Cell.conductor
circuit.mat[15][9] = cpu.Cell.transistor
circuit.mat[15][14] = cpu.Cell.conductor
circuit.mat[15][16] = cpu.Cell.conductor
circuit.mat[15][22] = cpu.Cell.conductor
circuit.mat[16][7] = cpu.Cell.conductor
circuit.mat[16][9] = cpu.Cell.conductor
circuit.mat[16][10] = cpu.Cell.resistor
circuit.mat[16][11] = cpu.Cell.conductor
circuit.mat[16][12] = cpu.Cell.live
circuit.mat[16][14] = cpu.Cell.conductor
circuit.mat[16][16] = cpu.Cell.conductor
circuit.mat[16][22] = cpu.Cell.conductor
circuit.mat[17][7] = cpu.Cell.conductor
circuit.mat[17][9] = cpu.Cell.conductor
circuit.mat[17][14] = cpu.Cell.conductor
circuit.mat[17][16] = cpu.Cell.transistor_gate
circuit.mat[17][22] = cpu.Cell.conductor
circuit.mat[18][7] = cpu.Cell.conductor
circuit.mat[18][9] = cpu.Cell.conductor
circuit.mat[18][10] = cpu.Cell.conductor
circuit.mat[18][11] = cpu.Cell.conductor
circuit.mat[18][12] = cpu.Cell.conductor
circuit.mat[18][13] = cpu.Cell.conductor
circuit.mat[18][14] = cpu.Cell.overlap
circuit.mat[18][15] = cpu.Cell.conductor
circuit.mat[18][16] = cpu.Cell.transistor
circuit.mat[18][17] = cpu.Cell.conductor
circuit.mat[18][18] = cpu.Cell.conductor
circuit.mat[18][22] = cpu.Cell.conductor
circuit.mat[19][7] = cpu.Cell.conductor
circuit.mat[19][14] = cpu.Cell.transistor_gate
circuit.mat[19][18] = cpu.Cell.conductor
circuit.mat[19][19] = cpu.Cell.conductor
circuit.mat[19][20] = cpu.Cell.conductor
circuit.mat[19][21] = cpu.Cell.conductor
circuit.mat[19][22] = cpu.Cell.conductor
circuit.mat[20][7] = cpu.Cell.conductor
circuit.mat[20][8] = cpu.Cell.conductor
circuit.mat[20][9] = cpu.Cell.conductor
circuit.mat[20][10] = cpu.Cell.conductor
circuit.mat[20][11] = cpu.Cell.conductor
circuit.mat[20][12] = cpu.Cell.conductor
circuit.mat[20][13] = cpu.Cell.conductor
circuit.mat[20][14] = cpu.Cell.transistor
circuit.mat[20][15] = cpu.Cell.conductor
circuit.mat[20][16] = cpu.Cell.conductor
circuit.mat[20][17] = cpu.Cell.conductor
circuit.mat[20][18] = cpu.Cell.conductor

circuit.generate_groups()
circuit.update_transistors()
circuit.update_resistor_groups()

copy_region = [(0, 0), (0, 0)]
copy_mode = CopyMode.inactive

resize(res)
pres = pygame.display.list_modes()[0]
# pygame.key.set_repeat(500, 50)
clock = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if   event.key == K_ESCAPE:
				if copy_mode is not CopyMode.inactive:
					copy_mode = CopyMode.inactive
				else:
					running = False
			elif event.key == K_F11: toggleFullscreen()
			elif event.key == K_d:
				# d for conDuctor
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					paint_mode = cpu.Cell.insulator
				else:
					paint_mode = cpu.Cell.conductor
			elif event.key == K_e:
				# e for sourcE
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					paint_mode = cpu.Cell.ground
				else:
					paint_mode = cpu.Cell.live
			elif event.key == K_s: print(end=circuit.generate_source())
			elif event.key == K_r: circuit.update_resistor_groups()
			elif event.key == K_g:
				circuit.generate_groups()
				if not event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					circuit.update_transistors()
					circuit.update_resistor_groups()
			elif event.key == K_c:
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					copy_mode = CopyMode.ready
				else:
					copy_mode = CopyMode.active
			elif event.key == K_t:
				circuit.update_transistors()
				if not event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					circuit.update_resistor_groups()
			elif event.key == K_i:
				mouse_pos = pygame.mouse.get_pos()
				x, y = from_screen_space(mouse_pos, view_rect, size)

				if (x, y) not in circuit.static_groups: continue

				print('GROUP INFO')

				static_group = circuit.static_groups[x, y]
				print(static_group)
				if static_group.override is None: print(); continue

				dyn_group = static_group.override
				print(dyn_group)
				if dyn_group.resistor_override is None: print(); continue

				print(dyn_group.resistor_override)

				print()

		elif event.type == VIDEORESIZE:
			if not display.get_flags()&FULLSCREEN: resize(event.size)
		elif event.type == QUIT: running = False
		elif event.type == MOUSEBUTTONDOWN:

			if event.button in (4, 5):
				if pygame.key.get_mods() & (KMOD_LCTRL|KMOD_RCTRL):
					old_size = size

					if event.button == 5:
						size *= ZOOM_FAC_NUM
						size //= ZOOM_FAC_DEN
						if size < 1: size = 1
					elif event.button == 4:
						if size <= 1: size += 1
						size *= ZOOM_FAC_DEN
						size //= ZOOM_FAC_NUM

					view_rect[0] *= size
					view_rect[0] //= old_size
					# top_left of the rect should move proportionally
				else:
					delta = event.button*2-9
					val = paint_mode.value + delta - 1
					val %= len(cpu.Cell)
					val += 1
					paint_mode = cpu.Cell(val)

			elif event.button == 1:
				click_pos = from_screen_space(event.pos, view_rect, size)

				if copy_mode is CopyMode.active:
					copy_region = [click_pos, click_pos]
					copy_mode = CopyMode.select
				elif copy_mode is CopyMode.ready:
					# paste

					copy_h = copy_region[1][1] - copy_region[0][1] + 1
					copy_w = copy_region[1][0] - copy_region[0][0] + 1

					# no overlap safety.
					# The simplest type of copy will work
					for dest_row, src_row in zip(
						circuit.mat[click_pos[1]:click_pos[1] + copy_h],
						circuit.mat[copy_region[0][1]:copy_region[1][1]+1],
					):

						dest_row[click_pos[0]:click_pos[0] + copy_w] = (
							src_row[copy_region[0][0]:copy_region[1][0]+1]
						)

					copy_mode = CopyMode.inactive
				else:
					key_mods = pygame.key.get_mods()
					if key_mods & (KMOD_LALT|KMOD_RALT):
						x, y = click_pos
						paint_mode = circuit.mat[y][x]
					else:
						dragging = True
						if not pygame.key.get_mods()&(KMOD_LSHIFT|KMOD_RSHIFT):
							x, y = click_pos
							circuit.mat[y][x] = paint_mode
			elif event.button == 3:
				x, y = from_screen_space(event.pos, view_rect, size)
				if (x, y) in circuit.static_groups:
					selected_group = circuit.static_groups[x, y].get_resistor_override()
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				dragging = False
				if copy_mode is CopyMode.select:
					copy_mode = CopyMode.ready
			elif event.button == 3:
				x, y = from_screen_space(event.pos, view_rect, size)
				selected_group = None
		elif event.type == MOUSEMOTION:
			if copy_mode is CopyMode.select:
				if copy_region:
					copy_region[1] = (
						from_screen_space(event.pos, view_rect, size)
					)
			elif dragging:
				if pygame.key.get_mods() & (KMOD_LSHIFT|KMOD_RSHIFT):
					view_rect.move_ip(-event.rel[0], -event.rel[1])
				else:
					x, y = from_screen_space(event.pos, view_rect, size)
					circuit.mat[y][x] = paint_mode

	updateDisplay()
	ticks += clock.tick(fps)
