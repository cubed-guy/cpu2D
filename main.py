# DONE: Draw to cells
# DONE: Generate Groups
# DONE: Update Group Values
# TODO: Update Transistor States
# TODO: Optimise matrix rendering
# TODO: Rewind

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

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

w, h = res = (1280, 720)

def updateStat(msg = None, update = True):
	# call this if you have a long loop that'll taking too long
	rect = (0, h-20, w, 21)
	display.fill(c-0, rect)

	mouse_pos = pygame.mouse.get_pos()
	cell = from_screen_space(mouse_pos, view_rect, size)
	tsurf = sfont.render(msg or f'{cell} {paint_mode} {selected_group and selected_group.cells}', True, c--1)
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

view_rect = pygame.Rect(0, 0, w, h)
dragging = False
ticks = 0

selected_group = None
size = 64
paint_mode = cpu.Cell.conductor
print(paint_mode)

circuit = cpu.Circuit(500, 500)

resize(res)
pres = pygame.display.list_modes()[0]
# pygame.key.set_repeat(500, 50)
clock = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if   event.key == K_ESCAPE: running = False
			elif event.key == K_F11: toggleFullscreen()
			elif event.key == K_g: circuit.generate_groups()

		elif event.type == VIDEORESIZE:
			if not display.get_flags()&FULLSCREEN: resize(event.size)
		elif event.type == QUIT: running = False
		elif event.type == MOUSEBUTTONDOWN:

			if event.button in (4, 5):
				delta = event.button*2-9
				if pygame.key.get_mods() & (KMOD_LCTRL|KMOD_RCTRL):
					size += delta
				else:
					val = paint_mode.value + delta - 1
					val %= len(cpu.Cell)
					val += 1
					paint_mode = cpu.Cell(val)
					print(paint_mode.value, paint_mode)

			elif event.button == 1:
				dragging = True
				if not pygame.key.get_mods() & (KMOD_LSHIFT|KMOD_RSHIFT):
					x, y = from_screen_space(event.pos, view_rect, size)
					circuit.mat[y][x] = paint_mode
			elif event.button == 3:
				x, y = from_screen_space(event.pos, view_rect, size)
				if (x, y) in circuit.groups:
					selected_group = circuit.groups[x, y]
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				dragging = False
			elif event.button == 3:
				x, y = from_screen_space(event.pos, view_rect, size)
				selected_group = None
		elif event.type == MOUSEMOTION:
			if dragging:
				if pygame.key.get_mods() & (KMOD_LSHIFT|KMOD_RSHIFT):
					view_rect.move_ip(-event.rel[0], -event.rel[1])
				else:
					x, y = from_screen_space(event.pos, view_rect, size)
					circuit.mat[y][x] = paint_mode

	updateDisplay()
	ticks += clock.tick(fps)
