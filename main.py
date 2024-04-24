# DONE: Draw to cells
# DONE: Generate Groups
# DONE: Update Group Values
# DONE: Update Transistor States
# DONE: Resistors are not insulators
# DONE: Copy-paste support
# DONE: Overlap Support
# DONE: Optimise Resistor Updates
# DONE: Fill Area
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
WHEEL_FAC = 7

w, h = res = (1280, 800)

def updateStat(msg = None, update = True):
	# call this if you have a long loop that'll taking too long
	rect = (0, h-20, w, 21)
	display.fill(c-0, rect)

	mouse_pos = pygame.mouse.get_pos()
	cell = from_screen_space(mouse_pos, view_rect, size)
	tsurf = sfont.render(msg or
		f'{size} {cell} {paint_mode} '
		f'{type(selected_group)} '
		f'{select_region} {select_state} {select_mode}',
	True, c--1)
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

	if select_state in (SelectState.selecting, SelectState.ready):
		surf = circuit.render(size, view_rect, selected_group, selected_region=select_region)
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

class SelectState(Enum):
	inactive = auto()  # nothing is happening
	active = auto()    # ready to strt selecting
	selecting = auto() # selecting /// dragging
	ready = auto()     # select area is ready

class SelectMode(Enum):
	undecided = auto()
	fill = auto()
	copy = auto()

view_rect = pygame.Rect(0, 0, w, h)
dragging = False
ticks = 0

selected_group = None
size = 36
paint_mode = cpu.Cell.conductor
circuit = cpu.Circuit(500, 500)
select_region = [(0, 0), (0, 0)]
select_state = SelectState.inactive
select_mode = SelectMode.undecided
scrolling = False

circuit.mat[4][10] = cpu.Cell.ground
circuit.mat[4][11] = cpu.Cell.conductor
circuit.mat[4][15] = cpu.Cell.transistor_gate
circuit.mat[4][16] = cpu.Cell.ground
circuit.mat[4][56] = cpu.Cell.conductor
circuit.mat[4][57] = cpu.Cell.overlap
circuit.mat[4][58] = cpu.Cell.overlap
circuit.mat[4][59] = cpu.Cell.overlap
circuit.mat[4][60] = cpu.Cell.overlap
circuit.mat[4][61] = cpu.Cell.overlap
circuit.mat[4][62] = cpu.Cell.overlap
circuit.mat[4][63] = cpu.Cell.overlap
circuit.mat[4][64] = cpu.Cell.overlap
circuit.mat[4][65] = cpu.Cell.overlap
circuit.mat[5][11] = cpu.Cell.resistor
circuit.mat[5][12] = cpu.Cell.conductor
circuit.mat[5][13] = cpu.Cell.conductor
circuit.mat[5][14] = cpu.Cell.conductor
circuit.mat[5][15] = cpu.Cell.transistor
circuit.mat[5][31] = cpu.Cell.conductor
circuit.mat[5][56] = cpu.Cell.overlap
circuit.mat[5][57] = cpu.Cell.conductor
circuit.mat[5][58] = cpu.Cell.overlap
circuit.mat[5][59] = cpu.Cell.overlap
circuit.mat[5][60] = cpu.Cell.overlap
circuit.mat[5][61] = cpu.Cell.overlap
circuit.mat[5][62] = cpu.Cell.overlap
circuit.mat[5][63] = cpu.Cell.overlap
circuit.mat[5][64] = cpu.Cell.overlap
circuit.mat[5][65] = cpu.Cell.overlap
circuit.mat[6][9] = cpu.Cell.live
circuit.mat[6][10] = cpu.Cell.transistor_gate
circuit.mat[6][12] = cpu.Cell.transistor_gate
circuit.mat[6][14] = cpu.Cell.transistor
circuit.mat[6][15] = cpu.Cell.conductor
circuit.mat[6][16] = cpu.Cell.live
circuit.mat[6][31] = cpu.Cell.conductor
circuit.mat[6][56] = cpu.Cell.overlap
circuit.mat[6][57] = cpu.Cell.overlap
circuit.mat[6][58] = cpu.Cell.conductor
circuit.mat[6][59] = cpu.Cell.overlap
circuit.mat[6][60] = cpu.Cell.overlap
circuit.mat[6][61] = cpu.Cell.overlap
circuit.mat[6][62] = cpu.Cell.overlap
circuit.mat[6][63] = cpu.Cell.overlap
circuit.mat[6][64] = cpu.Cell.overlap
circuit.mat[6][65] = cpu.Cell.overlap
circuit.mat[7][10] = cpu.Cell.transistor
circuit.mat[7][11] = cpu.Cell.conductor
circuit.mat[7][12] = cpu.Cell.transistor
circuit.mat[7][13] = cpu.Cell.conductor
circuit.mat[7][14] = cpu.Cell.transistor_gate
circuit.mat[7][31] = cpu.Cell.conductor
circuit.mat[7][56] = cpu.Cell.overlap
circuit.mat[7][57] = cpu.Cell.overlap
circuit.mat[7][58] = cpu.Cell.overlap
circuit.mat[7][59] = cpu.Cell.conductor
circuit.mat[7][60] = cpu.Cell.overlap
circuit.mat[7][61] = cpu.Cell.overlap
circuit.mat[7][62] = cpu.Cell.overlap
circuit.mat[7][63] = cpu.Cell.overlap
circuit.mat[7][64] = cpu.Cell.overlap
circuit.mat[7][65] = cpu.Cell.overlap
circuit.mat[8][9] = cpu.Cell.live
circuit.mat[8][10] = cpu.Cell.conductor
circuit.mat[8][14] = cpu.Cell.resistor
circuit.mat[8][15] = cpu.Cell.conductor
circuit.mat[8][16] = cpu.Cell.ground
circuit.mat[8][25] = cpu.Cell.live
circuit.mat[8][26] = cpu.Cell.conductor
circuit.mat[8][28] = cpu.Cell.ground
circuit.mat[8][29] = cpu.Cell.conductor
circuit.mat[8][31] = cpu.Cell.conductor
circuit.mat[8][33] = cpu.Cell.transistor_gate
circuit.mat[8][34] = cpu.Cell.conductor
circuit.mat[8][35] = cpu.Cell.conductor
circuit.mat[8][36] = cpu.Cell.conductor
circuit.mat[8][37] = cpu.Cell.resistor
circuit.mat[8][38] = cpu.Cell.conductor
circuit.mat[8][56] = cpu.Cell.overlap
circuit.mat[8][57] = cpu.Cell.overlap
circuit.mat[8][58] = cpu.Cell.overlap
circuit.mat[8][59] = cpu.Cell.overlap
circuit.mat[8][60] = cpu.Cell.conductor
circuit.mat[8][61] = cpu.Cell.overlap
circuit.mat[8][62] = cpu.Cell.overlap
circuit.mat[8][63] = cpu.Cell.overlap
circuit.mat[8][64] = cpu.Cell.overlap
circuit.mat[8][65] = cpu.Cell.overlap
circuit.mat[9][26] = cpu.Cell.resistor
circuit.mat[9][29] = cpu.Cell.resistor
circuit.mat[9][30] = cpu.Cell.conductor
circuit.mat[9][31] = cpu.Cell.conductor
circuit.mat[9][32] = cpu.Cell.conductor
circuit.mat[9][33] = cpu.Cell.transistor
circuit.mat[9][36] = cpu.Cell.conductor
circuit.mat[9][38] = cpu.Cell.ground
circuit.mat[9][56] = cpu.Cell.overlap
circuit.mat[9][57] = cpu.Cell.overlap
circuit.mat[9][58] = cpu.Cell.overlap
circuit.mat[9][59] = cpu.Cell.overlap
circuit.mat[9][60] = cpu.Cell.overlap
circuit.mat[9][61] = cpu.Cell.conductor
circuit.mat[9][62] = cpu.Cell.overlap
circuit.mat[9][63] = cpu.Cell.overlap
circuit.mat[9][64] = cpu.Cell.overlap
circuit.mat[9][65] = cpu.Cell.overlap
circuit.mat[10][23] = cpu.Cell.conductor
circuit.mat[10][24] = cpu.Cell.conductor
circuit.mat[10][25] = cpu.Cell.transistor
circuit.mat[10][26] = cpu.Cell.conductor
circuit.mat[10][27] = cpu.Cell.conductor
circuit.mat[10][28] = cpu.Cell.transistor_gate
circuit.mat[10][30] = cpu.Cell.transistor_gate
circuit.mat[10][32] = cpu.Cell.transistor
circuit.mat[10][33] = cpu.Cell.conductor
circuit.mat[10][34] = cpu.Cell.live
circuit.mat[10][36] = cpu.Cell.conductor
circuit.mat[10][56] = cpu.Cell.overlap
circuit.mat[10][57] = cpu.Cell.overlap
circuit.mat[10][58] = cpu.Cell.overlap
circuit.mat[10][59] = cpu.Cell.overlap
circuit.mat[10][60] = cpu.Cell.overlap
circuit.mat[10][61] = cpu.Cell.overlap
circuit.mat[10][62] = cpu.Cell.conductor
circuit.mat[10][63] = cpu.Cell.overlap
circuit.mat[10][64] = cpu.Cell.overlap
circuit.mat[10][65] = cpu.Cell.overlap
circuit.mat[11][23] = cpu.Cell.conductor
circuit.mat[11][25] = cpu.Cell.transistor_gate
circuit.mat[11][28] = cpu.Cell.transistor
circuit.mat[11][29] = cpu.Cell.conductor
circuit.mat[11][30] = cpu.Cell.transistor
circuit.mat[11][31] = cpu.Cell.conductor
circuit.mat[11][32] = cpu.Cell.transistor_gate
circuit.mat[11][36] = cpu.Cell.conductor
circuit.mat[11][56] = cpu.Cell.overlap
circuit.mat[11][57] = cpu.Cell.overlap
circuit.mat[11][58] = cpu.Cell.overlap
circuit.mat[11][59] = cpu.Cell.overlap
circuit.mat[11][60] = cpu.Cell.overlap
circuit.mat[11][61] = cpu.Cell.overlap
circuit.mat[11][62] = cpu.Cell.overlap
circuit.mat[11][63] = cpu.Cell.conductor
circuit.mat[11][64] = cpu.Cell.overlap
circuit.mat[11][65] = cpu.Cell.overlap
circuit.mat[12][23] = cpu.Cell.conductor
circuit.mat[12][25] = cpu.Cell.conductor
circuit.mat[12][27] = cpu.Cell.live
circuit.mat[12][28] = cpu.Cell.conductor
circuit.mat[12][32] = cpu.Cell.resistor
circuit.mat[12][33] = cpu.Cell.conductor
circuit.mat[12][34] = cpu.Cell.ground
circuit.mat[12][36] = cpu.Cell.conductor
circuit.mat[12][56] = cpu.Cell.overlap
circuit.mat[12][57] = cpu.Cell.overlap
circuit.mat[12][58] = cpu.Cell.overlap
circuit.mat[12][59] = cpu.Cell.overlap
circuit.mat[12][60] = cpu.Cell.overlap
circuit.mat[12][61] = cpu.Cell.overlap
circuit.mat[12][62] = cpu.Cell.overlap
circuit.mat[12][63] = cpu.Cell.overlap
circuit.mat[12][64] = cpu.Cell.conductor
circuit.mat[12][65] = cpu.Cell.overlap
circuit.mat[13][23] = cpu.Cell.conductor
circuit.mat[13][25] = cpu.Cell.conductor
circuit.mat[13][36] = cpu.Cell.conductor
circuit.mat[13][56] = cpu.Cell.overlap
circuit.mat[13][57] = cpu.Cell.overlap
circuit.mat[13][58] = cpu.Cell.overlap
circuit.mat[13][59] = cpu.Cell.overlap
circuit.mat[13][60] = cpu.Cell.overlap
circuit.mat[13][61] = cpu.Cell.overlap
circuit.mat[13][62] = cpu.Cell.overlap
circuit.mat[13][63] = cpu.Cell.overlap
circuit.mat[13][64] = cpu.Cell.overlap
circuit.mat[13][65] = cpu.Cell.conductor
circuit.mat[14][23] = cpu.Cell.conductor
circuit.mat[14][25] = cpu.Cell.conductor
circuit.mat[14][26] = cpu.Cell.conductor
circuit.mat[14][27] = cpu.Cell.conductor
circuit.mat[14][28] = cpu.Cell.conductor
circuit.mat[14][29] = cpu.Cell.conductor
circuit.mat[14][30] = cpu.Cell.conductor
circuit.mat[14][31] = cpu.Cell.conductor
circuit.mat[14][32] = cpu.Cell.conductor
circuit.mat[14][33] = cpu.Cell.conductor
circuit.mat[14][34] = cpu.Cell.conductor
circuit.mat[14][35] = cpu.Cell.transistor_gate
circuit.mat[14][36] = cpu.Cell.transistor
circuit.mat[14][56] = cpu.Cell.overlap
circuit.mat[14][57] = cpu.Cell.overlap
circuit.mat[14][58] = cpu.Cell.overlap
circuit.mat[14][59] = cpu.Cell.overlap
circuit.mat[14][60] = cpu.Cell.overlap
circuit.mat[14][61] = cpu.Cell.overlap
circuit.mat[14][62] = cpu.Cell.overlap
circuit.mat[14][63] = cpu.Cell.overlap
circuit.mat[14][64] = cpu.Cell.overlap
circuit.mat[14][65] = cpu.Cell.overlap
circuit.mat[15][23] = cpu.Cell.conductor
circuit.mat[15][28] = cpu.Cell.conductor
circuit.mat[15][36] = cpu.Cell.conductor
circuit.mat[15][55] = cpu.Cell.live
circuit.mat[15][56] = cpu.Cell.conductor
circuit.mat[15][57] = cpu.Cell.overlap
circuit.mat[15][58] = cpu.Cell.overlap
circuit.mat[15][59] = cpu.Cell.overlap
circuit.mat[15][60] = cpu.Cell.overlap
circuit.mat[15][61] = cpu.Cell.overlap
circuit.mat[15][62] = cpu.Cell.overlap
circuit.mat[15][63] = cpu.Cell.overlap
circuit.mat[15][64] = cpu.Cell.overlap
circuit.mat[15][65] = cpu.Cell.overlap
circuit.mat[16][23] = cpu.Cell.conductor
circuit.mat[16][24] = cpu.Cell.conductor
circuit.mat[16][25] = cpu.Cell.conductor
circuit.mat[16][26] = cpu.Cell.conductor
circuit.mat[16][27] = cpu.Cell.conductor
circuit.mat[16][28] = cpu.Cell.overlap
circuit.mat[16][29] = cpu.Cell.conductor
circuit.mat[16][30] = cpu.Cell.conductor
circuit.mat[16][31] = cpu.Cell.conductor
circuit.mat[16][32] = cpu.Cell.conductor
circuit.mat[16][33] = cpu.Cell.conductor
circuit.mat[16][34] = cpu.Cell.conductor
circuit.mat[16][35] = cpu.Cell.conductor
circuit.mat[16][36] = cpu.Cell.conductor
circuit.mat[16][57] = cpu.Cell.overlap
circuit.mat[16][58] = cpu.Cell.overlap
circuit.mat[16][59] = cpu.Cell.overlap
circuit.mat[16][60] = cpu.Cell.overlap
circuit.mat[16][61] = cpu.Cell.overlap
circuit.mat[16][62] = cpu.Cell.overlap
circuit.mat[16][63] = cpu.Cell.overlap
circuit.mat[16][64] = cpu.Cell.overlap
circuit.mat[16][65] = cpu.Cell.overlap
circuit.mat[17][28] = cpu.Cell.conductor
circuit.mat[17][30] = cpu.Cell.conductor
circuit.mat[17][55] = cpu.Cell.live
circuit.mat[17][56] = cpu.Cell.conductor
circuit.mat[17][57] = cpu.Cell.conductor
circuit.mat[17][58] = cpu.Cell.overlap
circuit.mat[17][59] = cpu.Cell.overlap
circuit.mat[17][60] = cpu.Cell.overlap
circuit.mat[17][61] = cpu.Cell.overlap
circuit.mat[17][62] = cpu.Cell.overlap
circuit.mat[17][63] = cpu.Cell.overlap
circuit.mat[17][64] = cpu.Cell.overlap
circuit.mat[17][65] = cpu.Cell.overlap
circuit.mat[18][28] = cpu.Cell.ground
circuit.mat[18][30] = cpu.Cell.ground
circuit.mat[18][58] = cpu.Cell.overlap
circuit.mat[18][59] = cpu.Cell.overlap
circuit.mat[18][60] = cpu.Cell.overlap
circuit.mat[18][61] = cpu.Cell.overlap
circuit.mat[18][62] = cpu.Cell.overlap
circuit.mat[18][63] = cpu.Cell.overlap
circuit.mat[18][64] = cpu.Cell.overlap
circuit.mat[18][65] = cpu.Cell.overlap
circuit.mat[19][55] = cpu.Cell.ground
circuit.mat[19][56] = cpu.Cell.conductor
circuit.mat[19][57] = cpu.Cell.conductor
circuit.mat[19][58] = cpu.Cell.conductor
circuit.mat[19][59] = cpu.Cell.overlap
circuit.mat[19][60] = cpu.Cell.overlap
circuit.mat[19][61] = cpu.Cell.overlap
circuit.mat[19][62] = cpu.Cell.overlap
circuit.mat[19][63] = cpu.Cell.overlap
circuit.mat[19][64] = cpu.Cell.overlap
circuit.mat[19][65] = cpu.Cell.overlap
circuit.mat[20][59] = cpu.Cell.overlap
circuit.mat[20][60] = cpu.Cell.overlap
circuit.mat[20][61] = cpu.Cell.overlap
circuit.mat[20][62] = cpu.Cell.overlap
circuit.mat[20][63] = cpu.Cell.overlap
circuit.mat[20][64] = cpu.Cell.overlap
circuit.mat[20][65] = cpu.Cell.overlap
circuit.mat[21][55] = cpu.Cell.live
circuit.mat[21][56] = cpu.Cell.conductor
circuit.mat[21][57] = cpu.Cell.conductor
circuit.mat[21][58] = cpu.Cell.conductor
circuit.mat[21][59] = cpu.Cell.conductor
circuit.mat[21][60] = cpu.Cell.overlap
circuit.mat[21][61] = cpu.Cell.overlap
circuit.mat[21][62] = cpu.Cell.overlap
circuit.mat[21][63] = cpu.Cell.overlap
circuit.mat[21][64] = cpu.Cell.overlap
circuit.mat[21][65] = cpu.Cell.overlap
circuit.mat[22][60] = cpu.Cell.overlap
circuit.mat[22][61] = cpu.Cell.overlap
circuit.mat[22][62] = cpu.Cell.overlap
circuit.mat[22][63] = cpu.Cell.overlap
circuit.mat[22][64] = cpu.Cell.overlap
circuit.mat[22][65] = cpu.Cell.overlap
circuit.mat[23][28] = cpu.Cell.live
circuit.mat[23][55] = cpu.Cell.live
circuit.mat[23][56] = cpu.Cell.conductor
circuit.mat[23][57] = cpu.Cell.conductor
circuit.mat[23][58] = cpu.Cell.conductor
circuit.mat[23][59] = cpu.Cell.conductor
circuit.mat[23][60] = cpu.Cell.conductor
circuit.mat[23][61] = cpu.Cell.overlap
circuit.mat[23][62] = cpu.Cell.overlap
circuit.mat[23][63] = cpu.Cell.overlap
circuit.mat[23][64] = cpu.Cell.overlap
circuit.mat[23][65] = cpu.Cell.overlap
circuit.mat[24][28] = cpu.Cell.conductor
circuit.mat[24][61] = cpu.Cell.overlap
circuit.mat[24][62] = cpu.Cell.overlap
circuit.mat[24][63] = cpu.Cell.overlap
circuit.mat[24][64] = cpu.Cell.overlap
circuit.mat[24][65] = cpu.Cell.overlap
circuit.mat[25][11] = cpu.Cell.conductor
circuit.mat[25][12] = cpu.Cell.conductor
circuit.mat[25][13] = cpu.Cell.conductor
circuit.mat[25][14] = cpu.Cell.conductor
circuit.mat[25][15] = cpu.Cell.conductor
circuit.mat[25][16] = cpu.Cell.conductor
circuit.mat[25][17] = cpu.Cell.conductor
circuit.mat[25][18] = cpu.Cell.conductor
circuit.mat[25][19] = cpu.Cell.conductor
circuit.mat[25][20] = cpu.Cell.conductor
circuit.mat[25][21] = cpu.Cell.conductor
circuit.mat[25][22] = cpu.Cell.conductor
circuit.mat[25][23] = cpu.Cell.transistor
circuit.mat[25][24] = cpu.Cell.conductor
circuit.mat[25][25] = cpu.Cell.conductor
circuit.mat[25][26] = cpu.Cell.conductor
circuit.mat[25][27] = cpu.Cell.transistor_gate
circuit.mat[25][28] = cpu.Cell.transistor
circuit.mat[25][55] = cpu.Cell.live
circuit.mat[25][56] = cpu.Cell.conductor
circuit.mat[25][57] = cpu.Cell.conductor
circuit.mat[25][58] = cpu.Cell.conductor
circuit.mat[25][59] = cpu.Cell.conductor
circuit.mat[25][60] = cpu.Cell.conductor
circuit.mat[25][61] = cpu.Cell.conductor
circuit.mat[25][62] = cpu.Cell.overlap
circuit.mat[25][63] = cpu.Cell.overlap
circuit.mat[25][64] = cpu.Cell.overlap
circuit.mat[25][65] = cpu.Cell.overlap
circuit.mat[26][11] = cpu.Cell.conductor
circuit.mat[26][23] = cpu.Cell.transistor_gate
circuit.mat[26][28] = cpu.Cell.conductor
circuit.mat[26][62] = cpu.Cell.overlap
circuit.mat[26][63] = cpu.Cell.overlap
circuit.mat[26][64] = cpu.Cell.overlap
circuit.mat[26][65] = cpu.Cell.overlap
circuit.mat[27][11] = cpu.Cell.conductor
circuit.mat[27][20] = cpu.Cell.live
circuit.mat[27][21] = cpu.Cell.conductor
circuit.mat[27][22] = cpu.Cell.resistor
circuit.mat[27][23] = cpu.Cell.conductor
circuit.mat[27][24] = cpu.Cell.transistor
circuit.mat[27][25] = cpu.Cell.conductor
circuit.mat[27][26] = cpu.Cell.ground
circuit.mat[27][28] = cpu.Cell.conductor
circuit.mat[27][55] = cpu.Cell.live
circuit.mat[27][56] = cpu.Cell.conductor
circuit.mat[27][57] = cpu.Cell.conductor
circuit.mat[27][58] = cpu.Cell.conductor
circuit.mat[27][59] = cpu.Cell.conductor
circuit.mat[27][60] = cpu.Cell.conductor
circuit.mat[27][61] = cpu.Cell.conductor
circuit.mat[27][62] = cpu.Cell.conductor
circuit.mat[27][63] = cpu.Cell.overlap
circuit.mat[27][64] = cpu.Cell.overlap
circuit.mat[27][65] = cpu.Cell.overlap
circuit.mat[28][11] = cpu.Cell.conductor
circuit.mat[28][24] = cpu.Cell.transistor_gate
circuit.mat[28][28] = cpu.Cell.conductor
circuit.mat[28][63] = cpu.Cell.overlap
circuit.mat[28][64] = cpu.Cell.overlap
circuit.mat[28][65] = cpu.Cell.overlap
circuit.mat[29][11] = cpu.Cell.conductor
circuit.mat[29][16] = cpu.Cell.ground
circuit.mat[29][18] = cpu.Cell.conductor
circuit.mat[29][19] = cpu.Cell.conductor
circuit.mat[29][20] = cpu.Cell.conductor
circuit.mat[29][21] = cpu.Cell.conductor
circuit.mat[29][22] = cpu.Cell.conductor
circuit.mat[29][23] = cpu.Cell.conductor
circuit.mat[29][24] = cpu.Cell.conductor
circuit.mat[29][25] = cpu.Cell.conductor
circuit.mat[29][26] = cpu.Cell.conductor
circuit.mat[29][27] = cpu.Cell.conductor
circuit.mat[29][28] = cpu.Cell.overlap
circuit.mat[29][29] = cpu.Cell.conductor
circuit.mat[29][30] = cpu.Cell.conductor
circuit.mat[29][55] = cpu.Cell.live
circuit.mat[29][56] = cpu.Cell.conductor
circuit.mat[29][57] = cpu.Cell.conductor
circuit.mat[29][58] = cpu.Cell.conductor
circuit.mat[29][59] = cpu.Cell.conductor
circuit.mat[29][60] = cpu.Cell.conductor
circuit.mat[29][61] = cpu.Cell.conductor
circuit.mat[29][62] = cpu.Cell.conductor
circuit.mat[29][63] = cpu.Cell.conductor
circuit.mat[29][64] = cpu.Cell.overlap
circuit.mat[29][65] = cpu.Cell.overlap
circuit.mat[30][11] = cpu.Cell.conductor
circuit.mat[30][16] = cpu.Cell.conductor
circuit.mat[30][18] = cpu.Cell.transistor_gate
circuit.mat[30][24] = cpu.Cell.conductor
circuit.mat[30][28] = cpu.Cell.conductor
circuit.mat[30][64] = cpu.Cell.overlap
circuit.mat[30][65] = cpu.Cell.overlap
circuit.mat[31][11] = cpu.Cell.conductor
circuit.mat[31][13] = cpu.Cell.ground
circuit.mat[31][16] = cpu.Cell.transistor
circuit.mat[31][17] = cpu.Cell.conductor
circuit.mat[31][18] = cpu.Cell.transistor
circuit.mat[31][22] = cpu.Cell.ground
circuit.mat[31][24] = cpu.Cell.conductor
circuit.mat[31][28] = cpu.Cell.conductor
circuit.mat[31][55] = cpu.Cell.live
circuit.mat[31][56] = cpu.Cell.conductor
circuit.mat[31][57] = cpu.Cell.conductor
circuit.mat[31][58] = cpu.Cell.conductor
circuit.mat[31][59] = cpu.Cell.conductor
circuit.mat[31][60] = cpu.Cell.conductor
circuit.mat[31][61] = cpu.Cell.conductor
circuit.mat[31][62] = cpu.Cell.conductor
circuit.mat[31][63] = cpu.Cell.conductor
circuit.mat[31][64] = cpu.Cell.conductor
circuit.mat[31][65] = cpu.Cell.overlap
circuit.mat[32][11] = cpu.Cell.conductor
circuit.mat[32][13] = cpu.Cell.conductor
circuit.mat[32][16] = cpu.Cell.transistor_gate
circuit.mat[32][18] = cpu.Cell.conductor
circuit.mat[32][22] = cpu.Cell.conductor
circuit.mat[32][24] = cpu.Cell.conductor
circuit.mat[32][26] = cpu.Cell.transistor_gate
circuit.mat[32][27] = cpu.Cell.conductor
circuit.mat[32][28] = cpu.Cell.conductor
circuit.mat[32][29] = cpu.Cell.resistor
circuit.mat[32][65] = cpu.Cell.overlap
circuit.mat[33][11] = cpu.Cell.conductor
circuit.mat[33][13] = cpu.Cell.transistor
circuit.mat[33][14] = cpu.Cell.transistor_gate
circuit.mat[33][16] = cpu.Cell.conductor
circuit.mat[33][18] = cpu.Cell.conductor
circuit.mat[33][22] = cpu.Cell.resistor
circuit.mat[33][23] = cpu.Cell.conductor
circuit.mat[33][24] = cpu.Cell.conductor
circuit.mat[33][25] = cpu.Cell.conductor
circuit.mat[33][26] = cpu.Cell.transistor
circuit.mat[33][29] = cpu.Cell.conductor
circuit.mat[33][55] = cpu.Cell.live
circuit.mat[33][56] = cpu.Cell.conductor
circuit.mat[33][57] = cpu.Cell.conductor
circuit.mat[33][58] = cpu.Cell.conductor
circuit.mat[33][59] = cpu.Cell.conductor
circuit.mat[33][60] = cpu.Cell.conductor
circuit.mat[33][61] = cpu.Cell.conductor
circuit.mat[33][62] = cpu.Cell.conductor
circuit.mat[33][63] = cpu.Cell.conductor
circuit.mat[33][64] = cpu.Cell.conductor
circuit.mat[33][65] = cpu.Cell.conductor
circuit.mat[34][11] = cpu.Cell.conductor
circuit.mat[34][12] = cpu.Cell.conductor
circuit.mat[34][13] = cpu.Cell.conductor
circuit.mat[34][14] = cpu.Cell.conductor
circuit.mat[34][15] = cpu.Cell.conductor
circuit.mat[34][16] = cpu.Cell.conductor
circuit.mat[34][18] = cpu.Cell.conductor
circuit.mat[34][19] = cpu.Cell.conductor
circuit.mat[34][20] = cpu.Cell.conductor
circuit.mat[34][21] = cpu.Cell.transistor_gate
circuit.mat[34][23] = cpu.Cell.transistor_gate
circuit.mat[34][25] = cpu.Cell.transistor
circuit.mat[34][26] = cpu.Cell.conductor
circuit.mat[34][27] = cpu.Cell.live
circuit.mat[34][29] = cpu.Cell.ground
circuit.mat[35][13] = cpu.Cell.resistor
circuit.mat[35][18] = cpu.Cell.resistor
circuit.mat[35][21] = cpu.Cell.transistor
circuit.mat[35][22] = cpu.Cell.conductor
circuit.mat[35][23] = cpu.Cell.transistor
circuit.mat[35][24] = cpu.Cell.conductor
circuit.mat[35][25] = cpu.Cell.transistor_gate
circuit.mat[36][13] = cpu.Cell.conductor
circuit.mat[36][17] = cpu.Cell.live
circuit.mat[36][18] = cpu.Cell.conductor
circuit.mat[36][20] = cpu.Cell.live
circuit.mat[36][21] = cpu.Cell.conductor
circuit.mat[36][25] = cpu.Cell.resistor
circuit.mat[36][26] = cpu.Cell.conductor
circuit.mat[36][27] = cpu.Cell.ground
circuit.mat[37][13] = cpu.Cell.live
circuit.mat[4][10] = cpu.Cell.ground
circuit.mat[4][11] = cpu.Cell.conductor
circuit.mat[4][15] = cpu.Cell.transistor_gate
circuit.mat[4][16] = cpu.Cell.ground
circuit.mat[4][56] = cpu.Cell.conductor
circuit.mat[4][57] = cpu.Cell.overlap
circuit.mat[4][58] = cpu.Cell.overlap
circuit.mat[4][59] = cpu.Cell.overlap
circuit.mat[4][60] = cpu.Cell.overlap
circuit.mat[4][61] = cpu.Cell.overlap
circuit.mat[4][62] = cpu.Cell.overlap
circuit.mat[4][63] = cpu.Cell.overlap
circuit.mat[4][64] = cpu.Cell.overlap
circuit.mat[4][65] = cpu.Cell.overlap
circuit.mat[5][11] = cpu.Cell.resistor
circuit.mat[5][12] = cpu.Cell.conductor
circuit.mat[5][13] = cpu.Cell.conductor
circuit.mat[5][14] = cpu.Cell.conductor
circuit.mat[5][15] = cpu.Cell.transistor
circuit.mat[5][31] = cpu.Cell.conductor
circuit.mat[5][56] = cpu.Cell.overlap
circuit.mat[5][57] = cpu.Cell.conductor
circuit.mat[5][58] = cpu.Cell.overlap
circuit.mat[5][59] = cpu.Cell.overlap
circuit.mat[5][60] = cpu.Cell.overlap
circuit.mat[5][61] = cpu.Cell.overlap
circuit.mat[5][62] = cpu.Cell.overlap
circuit.mat[5][63] = cpu.Cell.overlap
circuit.mat[5][64] = cpu.Cell.overlap
circuit.mat[5][65] = cpu.Cell.overlap
circuit.mat[6][9] = cpu.Cell.live
circuit.mat[6][10] = cpu.Cell.transistor_gate
circuit.mat[6][12] = cpu.Cell.transistor_gate
circuit.mat[6][14] = cpu.Cell.transistor
circuit.mat[6][15] = cpu.Cell.conductor
circuit.mat[6][16] = cpu.Cell.live
circuit.mat[6][31] = cpu.Cell.conductor
circuit.mat[6][56] = cpu.Cell.overlap
circuit.mat[6][57] = cpu.Cell.overlap
circuit.mat[6][58] = cpu.Cell.conductor
circuit.mat[6][59] = cpu.Cell.overlap
circuit.mat[6][60] = cpu.Cell.overlap
circuit.mat[6][61] = cpu.Cell.overlap
circuit.mat[6][62] = cpu.Cell.overlap
circuit.mat[6][63] = cpu.Cell.overlap
circuit.mat[6][64] = cpu.Cell.overlap
circuit.mat[6][65] = cpu.Cell.overlap
circuit.mat[7][10] = cpu.Cell.transistor
circuit.mat[7][11] = cpu.Cell.conductor
circuit.mat[7][12] = cpu.Cell.transistor
circuit.mat[7][13] = cpu.Cell.conductor
circuit.mat[7][14] = cpu.Cell.transistor_gate
circuit.mat[7][31] = cpu.Cell.conductor
circuit.mat[7][56] = cpu.Cell.overlap
circuit.mat[7][57] = cpu.Cell.overlap
circuit.mat[7][58] = cpu.Cell.overlap
circuit.mat[7][59] = cpu.Cell.conductor
circuit.mat[7][60] = cpu.Cell.overlap
circuit.mat[7][61] = cpu.Cell.overlap
circuit.mat[7][62] = cpu.Cell.overlap
circuit.mat[7][63] = cpu.Cell.overlap
circuit.mat[7][64] = cpu.Cell.overlap
circuit.mat[7][65] = cpu.Cell.overlap
circuit.mat[8][9] = cpu.Cell.live
circuit.mat[8][10] = cpu.Cell.conductor
circuit.mat[8][14] = cpu.Cell.resistor
circuit.mat[8][15] = cpu.Cell.conductor
circuit.mat[8][16] = cpu.Cell.ground
circuit.mat[8][25] = cpu.Cell.live
circuit.mat[8][26] = cpu.Cell.conductor
circuit.mat[8][28] = cpu.Cell.ground
circuit.mat[8][29] = cpu.Cell.conductor
circuit.mat[8][31] = cpu.Cell.conductor
circuit.mat[8][33] = cpu.Cell.transistor_gate
circuit.mat[8][34] = cpu.Cell.conductor
circuit.mat[8][35] = cpu.Cell.conductor
circuit.mat[8][36] = cpu.Cell.conductor
circuit.mat[8][37] = cpu.Cell.resistor
circuit.mat[8][38] = cpu.Cell.conductor
circuit.mat[8][56] = cpu.Cell.overlap
circuit.mat[8][57] = cpu.Cell.overlap
circuit.mat[8][58] = cpu.Cell.overlap
circuit.mat[8][59] = cpu.Cell.overlap
circuit.mat[8][60] = cpu.Cell.conductor
circuit.mat[8][61] = cpu.Cell.overlap
circuit.mat[8][62] = cpu.Cell.overlap
circuit.mat[8][63] = cpu.Cell.overlap
circuit.mat[8][64] = cpu.Cell.overlap
circuit.mat[8][65] = cpu.Cell.overlap
circuit.mat[9][26] = cpu.Cell.resistor
circuit.mat[9][29] = cpu.Cell.resistor
circuit.mat[9][30] = cpu.Cell.conductor
circuit.mat[9][31] = cpu.Cell.conductor
circuit.mat[9][32] = cpu.Cell.conductor
circuit.mat[9][33] = cpu.Cell.transistor
circuit.mat[9][36] = cpu.Cell.conductor
circuit.mat[9][38] = cpu.Cell.ground
circuit.mat[9][56] = cpu.Cell.overlap
circuit.mat[9][57] = cpu.Cell.overlap
circuit.mat[9][58] = cpu.Cell.overlap
circuit.mat[9][59] = cpu.Cell.overlap
circuit.mat[9][60] = cpu.Cell.overlap
circuit.mat[9][61] = cpu.Cell.conductor
circuit.mat[9][62] = cpu.Cell.overlap
circuit.mat[9][63] = cpu.Cell.overlap
circuit.mat[9][64] = cpu.Cell.overlap
circuit.mat[9][65] = cpu.Cell.overlap
circuit.mat[10][23] = cpu.Cell.conductor
circuit.mat[10][24] = cpu.Cell.conductor
circuit.mat[10][25] = cpu.Cell.transistor
circuit.mat[10][26] = cpu.Cell.conductor
circuit.mat[10][27] = cpu.Cell.conductor
circuit.mat[10][28] = cpu.Cell.transistor_gate
circuit.mat[10][30] = cpu.Cell.transistor_gate
circuit.mat[10][32] = cpu.Cell.transistor
circuit.mat[10][33] = cpu.Cell.conductor
circuit.mat[10][34] = cpu.Cell.live
circuit.mat[10][36] = cpu.Cell.conductor
circuit.mat[10][56] = cpu.Cell.overlap
circuit.mat[10][57] = cpu.Cell.overlap
circuit.mat[10][58] = cpu.Cell.overlap
circuit.mat[10][59] = cpu.Cell.overlap
circuit.mat[10][60] = cpu.Cell.overlap
circuit.mat[10][61] = cpu.Cell.overlap
circuit.mat[10][62] = cpu.Cell.conductor
circuit.mat[10][63] = cpu.Cell.overlap
circuit.mat[10][64] = cpu.Cell.overlap
circuit.mat[10][65] = cpu.Cell.overlap
circuit.mat[11][23] = cpu.Cell.conductor
circuit.mat[11][25] = cpu.Cell.transistor_gate
circuit.mat[11][28] = cpu.Cell.transistor
circuit.mat[11][29] = cpu.Cell.conductor
circuit.mat[11][30] = cpu.Cell.transistor
circuit.mat[11][31] = cpu.Cell.conductor
circuit.mat[11][32] = cpu.Cell.transistor_gate
circuit.mat[11][36] = cpu.Cell.conductor
circuit.mat[11][56] = cpu.Cell.overlap
circuit.mat[11][57] = cpu.Cell.overlap
circuit.mat[11][58] = cpu.Cell.overlap
circuit.mat[11][59] = cpu.Cell.overlap
circuit.mat[11][60] = cpu.Cell.overlap
circuit.mat[11][61] = cpu.Cell.overlap
circuit.mat[11][62] = cpu.Cell.overlap
circuit.mat[11][63] = cpu.Cell.conductor
circuit.mat[11][64] = cpu.Cell.overlap
circuit.mat[11][65] = cpu.Cell.overlap
circuit.mat[12][23] = cpu.Cell.conductor
circuit.mat[12][25] = cpu.Cell.conductor
circuit.mat[12][27] = cpu.Cell.live
circuit.mat[12][28] = cpu.Cell.conductor
circuit.mat[12][32] = cpu.Cell.resistor
circuit.mat[12][33] = cpu.Cell.conductor
circuit.mat[12][34] = cpu.Cell.ground
circuit.mat[12][36] = cpu.Cell.conductor
circuit.mat[12][56] = cpu.Cell.overlap
circuit.mat[12][57] = cpu.Cell.overlap
circuit.mat[12][58] = cpu.Cell.overlap
circuit.mat[12][59] = cpu.Cell.overlap
circuit.mat[12][60] = cpu.Cell.overlap
circuit.mat[12][61] = cpu.Cell.overlap
circuit.mat[12][62] = cpu.Cell.overlap
circuit.mat[12][63] = cpu.Cell.overlap
circuit.mat[12][64] = cpu.Cell.conductor
circuit.mat[12][65] = cpu.Cell.overlap
circuit.mat[13][23] = cpu.Cell.conductor
circuit.mat[13][25] = cpu.Cell.conductor
circuit.mat[13][36] = cpu.Cell.conductor
circuit.mat[13][56] = cpu.Cell.overlap
circuit.mat[13][57] = cpu.Cell.overlap
circuit.mat[13][58] = cpu.Cell.overlap
circuit.mat[13][59] = cpu.Cell.overlap
circuit.mat[13][60] = cpu.Cell.overlap
circuit.mat[13][61] = cpu.Cell.overlap
circuit.mat[13][62] = cpu.Cell.overlap
circuit.mat[13][63] = cpu.Cell.overlap
circuit.mat[13][64] = cpu.Cell.overlap
circuit.mat[13][65] = cpu.Cell.conductor
circuit.mat[14][23] = cpu.Cell.conductor
circuit.mat[14][25] = cpu.Cell.conductor
circuit.mat[14][26] = cpu.Cell.conductor
circuit.mat[14][27] = cpu.Cell.conductor
circuit.mat[14][28] = cpu.Cell.conductor
circuit.mat[14][29] = cpu.Cell.conductor
circuit.mat[14][30] = cpu.Cell.conductor
circuit.mat[14][31] = cpu.Cell.conductor
circuit.mat[14][32] = cpu.Cell.conductor
circuit.mat[14][33] = cpu.Cell.conductor
circuit.mat[14][34] = cpu.Cell.conductor
circuit.mat[14][35] = cpu.Cell.transistor_gate
circuit.mat[14][36] = cpu.Cell.transistor
circuit.mat[14][56] = cpu.Cell.overlap
circuit.mat[14][57] = cpu.Cell.overlap
circuit.mat[14][58] = cpu.Cell.overlap
circuit.mat[14][59] = cpu.Cell.overlap
circuit.mat[14][60] = cpu.Cell.overlap
circuit.mat[14][61] = cpu.Cell.overlap
circuit.mat[14][62] = cpu.Cell.overlap
circuit.mat[14][63] = cpu.Cell.overlap
circuit.mat[14][64] = cpu.Cell.overlap
circuit.mat[14][65] = cpu.Cell.overlap
circuit.mat[15][23] = cpu.Cell.conductor
circuit.mat[15][28] = cpu.Cell.conductor
circuit.mat[15][36] = cpu.Cell.conductor
circuit.mat[15][55] = cpu.Cell.live
circuit.mat[15][56] = cpu.Cell.conductor
circuit.mat[15][57] = cpu.Cell.overlap
circuit.mat[15][58] = cpu.Cell.overlap
circuit.mat[15][59] = cpu.Cell.overlap
circuit.mat[15][60] = cpu.Cell.overlap
circuit.mat[15][61] = cpu.Cell.overlap
circuit.mat[15][62] = cpu.Cell.overlap
circuit.mat[15][63] = cpu.Cell.overlap
circuit.mat[15][64] = cpu.Cell.overlap
circuit.mat[15][65] = cpu.Cell.overlap
circuit.mat[16][23] = cpu.Cell.conductor
circuit.mat[16][24] = cpu.Cell.conductor
circuit.mat[16][25] = cpu.Cell.conductor
circuit.mat[16][26] = cpu.Cell.conductor
circuit.mat[16][27] = cpu.Cell.conductor
circuit.mat[16][28] = cpu.Cell.overlap
circuit.mat[16][29] = cpu.Cell.conductor
circuit.mat[16][30] = cpu.Cell.conductor
circuit.mat[16][31] = cpu.Cell.conductor
circuit.mat[16][32] = cpu.Cell.conductor
circuit.mat[16][33] = cpu.Cell.conductor
circuit.mat[16][34] = cpu.Cell.conductor
circuit.mat[16][35] = cpu.Cell.conductor
circuit.mat[16][36] = cpu.Cell.conductor
circuit.mat[16][57] = cpu.Cell.overlap
circuit.mat[16][58] = cpu.Cell.overlap
circuit.mat[16][59] = cpu.Cell.overlap
circuit.mat[16][60] = cpu.Cell.overlap
circuit.mat[16][61] = cpu.Cell.overlap
circuit.mat[16][62] = cpu.Cell.overlap
circuit.mat[16][63] = cpu.Cell.overlap
circuit.mat[16][64] = cpu.Cell.overlap
circuit.mat[16][65] = cpu.Cell.overlap
circuit.mat[17][28] = cpu.Cell.conductor
circuit.mat[17][30] = cpu.Cell.conductor
circuit.mat[17][55] = cpu.Cell.live
circuit.mat[17][56] = cpu.Cell.conductor
circuit.mat[17][57] = cpu.Cell.conductor
circuit.mat[17][58] = cpu.Cell.overlap
circuit.mat[17][59] = cpu.Cell.overlap
circuit.mat[17][60] = cpu.Cell.overlap
circuit.mat[17][61] = cpu.Cell.overlap
circuit.mat[17][62] = cpu.Cell.overlap
circuit.mat[17][63] = cpu.Cell.overlap
circuit.mat[17][64] = cpu.Cell.overlap
circuit.mat[17][65] = cpu.Cell.overlap
circuit.mat[18][28] = cpu.Cell.ground
circuit.mat[18][30] = cpu.Cell.ground
circuit.mat[18][58] = cpu.Cell.overlap
circuit.mat[18][59] = cpu.Cell.overlap
circuit.mat[18][60] = cpu.Cell.overlap
circuit.mat[18][61] = cpu.Cell.overlap
circuit.mat[18][62] = cpu.Cell.overlap
circuit.mat[18][63] = cpu.Cell.overlap
circuit.mat[18][64] = cpu.Cell.overlap
circuit.mat[18][65] = cpu.Cell.overlap
circuit.mat[19][55] = cpu.Cell.ground
circuit.mat[19][56] = cpu.Cell.conductor
circuit.mat[19][57] = cpu.Cell.conductor
circuit.mat[19][58] = cpu.Cell.conductor
circuit.mat[19][59] = cpu.Cell.overlap
circuit.mat[19][60] = cpu.Cell.overlap
circuit.mat[19][61] = cpu.Cell.overlap
circuit.mat[19][62] = cpu.Cell.overlap
circuit.mat[19][63] = cpu.Cell.overlap
circuit.mat[19][64] = cpu.Cell.overlap
circuit.mat[19][65] = cpu.Cell.overlap
circuit.mat[20][59] = cpu.Cell.overlap
circuit.mat[20][60] = cpu.Cell.overlap
circuit.mat[20][61] = cpu.Cell.overlap
circuit.mat[20][62] = cpu.Cell.overlap
circuit.mat[20][63] = cpu.Cell.overlap
circuit.mat[20][64] = cpu.Cell.overlap
circuit.mat[20][65] = cpu.Cell.overlap
circuit.mat[21][55] = cpu.Cell.live
circuit.mat[21][56] = cpu.Cell.conductor
circuit.mat[21][57] = cpu.Cell.conductor
circuit.mat[21][58] = cpu.Cell.conductor
circuit.mat[21][59] = cpu.Cell.conductor
circuit.mat[21][60] = cpu.Cell.overlap
circuit.mat[21][61] = cpu.Cell.overlap
circuit.mat[21][62] = cpu.Cell.overlap
circuit.mat[21][63] = cpu.Cell.overlap
circuit.mat[21][64] = cpu.Cell.overlap
circuit.mat[21][65] = cpu.Cell.overlap
circuit.mat[22][60] = cpu.Cell.overlap
circuit.mat[22][61] = cpu.Cell.overlap
circuit.mat[22][62] = cpu.Cell.overlap
circuit.mat[22][63] = cpu.Cell.overlap
circuit.mat[22][64] = cpu.Cell.overlap
circuit.mat[22][65] = cpu.Cell.overlap
circuit.mat[23][28] = cpu.Cell.live
circuit.mat[23][55] = cpu.Cell.live
circuit.mat[23][56] = cpu.Cell.conductor
circuit.mat[23][57] = cpu.Cell.conductor
circuit.mat[23][58] = cpu.Cell.conductor
circuit.mat[23][59] = cpu.Cell.conductor
circuit.mat[23][60] = cpu.Cell.conductor
circuit.mat[23][61] = cpu.Cell.overlap
circuit.mat[23][62] = cpu.Cell.overlap
circuit.mat[23][63] = cpu.Cell.overlap
circuit.mat[23][64] = cpu.Cell.overlap
circuit.mat[23][65] = cpu.Cell.overlap
circuit.mat[24][28] = cpu.Cell.conductor
circuit.mat[24][61] = cpu.Cell.overlap
circuit.mat[24][62] = cpu.Cell.overlap
circuit.mat[24][63] = cpu.Cell.overlap
circuit.mat[24][64] = cpu.Cell.overlap
circuit.mat[24][65] = cpu.Cell.overlap
circuit.mat[25][11] = cpu.Cell.conductor
circuit.mat[25][12] = cpu.Cell.conductor
circuit.mat[25][13] = cpu.Cell.conductor
circuit.mat[25][14] = cpu.Cell.conductor
circuit.mat[25][15] = cpu.Cell.conductor
circuit.mat[25][16] = cpu.Cell.conductor
circuit.mat[25][17] = cpu.Cell.conductor
circuit.mat[25][18] = cpu.Cell.conductor
circuit.mat[25][19] = cpu.Cell.conductor
circuit.mat[25][20] = cpu.Cell.conductor
circuit.mat[25][21] = cpu.Cell.conductor
circuit.mat[25][22] = cpu.Cell.conductor
circuit.mat[25][23] = cpu.Cell.transistor
circuit.mat[25][24] = cpu.Cell.conductor
circuit.mat[25][25] = cpu.Cell.conductor
circuit.mat[25][26] = cpu.Cell.conductor
circuit.mat[25][27] = cpu.Cell.transistor_gate
circuit.mat[25][28] = cpu.Cell.transistor
circuit.mat[25][55] = cpu.Cell.live
circuit.mat[25][56] = cpu.Cell.conductor
circuit.mat[25][57] = cpu.Cell.conductor
circuit.mat[25][58] = cpu.Cell.conductor
circuit.mat[25][59] = cpu.Cell.conductor
circuit.mat[25][60] = cpu.Cell.conductor
circuit.mat[25][61] = cpu.Cell.conductor
circuit.mat[25][62] = cpu.Cell.overlap
circuit.mat[25][63] = cpu.Cell.overlap
circuit.mat[25][64] = cpu.Cell.overlap
circuit.mat[25][65] = cpu.Cell.overlap
circuit.mat[26][11] = cpu.Cell.conductor
circuit.mat[26][23] = cpu.Cell.transistor_gate
circuit.mat[26][28] = cpu.Cell.conductor
circuit.mat[26][62] = cpu.Cell.overlap
circuit.mat[26][63] = cpu.Cell.overlap
circuit.mat[26][64] = cpu.Cell.overlap
circuit.mat[26][65] = cpu.Cell.overlap
circuit.mat[27][11] = cpu.Cell.conductor
circuit.mat[27][20] = cpu.Cell.live
circuit.mat[27][21] = cpu.Cell.conductor
circuit.mat[27][22] = cpu.Cell.resistor
circuit.mat[27][23] = cpu.Cell.conductor
circuit.mat[27][24] = cpu.Cell.transistor
circuit.mat[27][25] = cpu.Cell.conductor
circuit.mat[27][26] = cpu.Cell.ground
circuit.mat[27][28] = cpu.Cell.conductor
circuit.mat[27][55] = cpu.Cell.live
circuit.mat[27][56] = cpu.Cell.conductor
circuit.mat[27][57] = cpu.Cell.conductor
circuit.mat[27][58] = cpu.Cell.conductor
circuit.mat[27][59] = cpu.Cell.conductor
circuit.mat[27][60] = cpu.Cell.conductor
circuit.mat[27][61] = cpu.Cell.conductor
circuit.mat[27][62] = cpu.Cell.conductor
circuit.mat[27][63] = cpu.Cell.overlap
circuit.mat[27][64] = cpu.Cell.overlap
circuit.mat[27][65] = cpu.Cell.overlap
circuit.mat[28][11] = cpu.Cell.conductor
circuit.mat[28][24] = cpu.Cell.transistor_gate
circuit.mat[28][28] = cpu.Cell.conductor
circuit.mat[28][63] = cpu.Cell.overlap
circuit.mat[28][64] = cpu.Cell.overlap
circuit.mat[28][65] = cpu.Cell.overlap
circuit.mat[29][11] = cpu.Cell.conductor
circuit.mat[29][16] = cpu.Cell.ground
circuit.mat[29][18] = cpu.Cell.conductor
circuit.mat[29][19] = cpu.Cell.conductor
circuit.mat[29][20] = cpu.Cell.conductor
circuit.mat[29][21] = cpu.Cell.conductor
circuit.mat[29][22] = cpu.Cell.conductor
circuit.mat[29][23] = cpu.Cell.conductor
circuit.mat[29][24] = cpu.Cell.conductor
circuit.mat[29][25] = cpu.Cell.conductor
circuit.mat[29][26] = cpu.Cell.conductor
circuit.mat[29][27] = cpu.Cell.conductor
circuit.mat[29][28] = cpu.Cell.overlap
circuit.mat[29][29] = cpu.Cell.conductor
circuit.mat[29][30] = cpu.Cell.conductor
circuit.mat[29][55] = cpu.Cell.live
circuit.mat[29][56] = cpu.Cell.conductor
circuit.mat[29][57] = cpu.Cell.conductor
circuit.mat[29][58] = cpu.Cell.conductor
circuit.mat[29][59] = cpu.Cell.conductor
circuit.mat[29][60] = cpu.Cell.conductor
circuit.mat[29][61] = cpu.Cell.conductor
circuit.mat[29][62] = cpu.Cell.conductor
circuit.mat[29][63] = cpu.Cell.conductor
circuit.mat[29][64] = cpu.Cell.overlap
circuit.mat[29][65] = cpu.Cell.overlap
circuit.mat[30][11] = cpu.Cell.conductor
circuit.mat[30][16] = cpu.Cell.conductor
circuit.mat[30][18] = cpu.Cell.transistor_gate
circuit.mat[30][24] = cpu.Cell.conductor
circuit.mat[30][28] = cpu.Cell.conductor
circuit.mat[30][64] = cpu.Cell.overlap
circuit.mat[30][65] = cpu.Cell.overlap
circuit.mat[31][11] = cpu.Cell.conductor
circuit.mat[31][13] = cpu.Cell.ground
circuit.mat[31][16] = cpu.Cell.transistor
circuit.mat[31][17] = cpu.Cell.conductor
circuit.mat[31][18] = cpu.Cell.transistor
circuit.mat[31][22] = cpu.Cell.ground
circuit.mat[31][24] = cpu.Cell.conductor
circuit.mat[31][28] = cpu.Cell.conductor
circuit.mat[31][55] = cpu.Cell.live
circuit.mat[31][56] = cpu.Cell.conductor
circuit.mat[31][57] = cpu.Cell.conductor
circuit.mat[31][58] = cpu.Cell.conductor
circuit.mat[31][59] = cpu.Cell.conductor
circuit.mat[31][60] = cpu.Cell.conductor
circuit.mat[31][61] = cpu.Cell.conductor
circuit.mat[31][62] = cpu.Cell.conductor
circuit.mat[31][63] = cpu.Cell.conductor
circuit.mat[31][64] = cpu.Cell.conductor
circuit.mat[31][65] = cpu.Cell.overlap
circuit.mat[32][11] = cpu.Cell.conductor
circuit.mat[32][13] = cpu.Cell.conductor
circuit.mat[32][16] = cpu.Cell.transistor_gate
circuit.mat[32][18] = cpu.Cell.conductor
circuit.mat[32][22] = cpu.Cell.conductor
circuit.mat[32][24] = cpu.Cell.conductor
circuit.mat[32][26] = cpu.Cell.transistor_gate
circuit.mat[32][27] = cpu.Cell.conductor
circuit.mat[32][28] = cpu.Cell.conductor
circuit.mat[32][29] = cpu.Cell.resistor
circuit.mat[32][65] = cpu.Cell.overlap
circuit.mat[33][11] = cpu.Cell.conductor
circuit.mat[33][13] = cpu.Cell.transistor
circuit.mat[33][14] = cpu.Cell.transistor_gate
circuit.mat[33][16] = cpu.Cell.conductor
circuit.mat[33][18] = cpu.Cell.conductor
circuit.mat[33][22] = cpu.Cell.resistor
circuit.mat[33][23] = cpu.Cell.conductor
circuit.mat[33][24] = cpu.Cell.conductor
circuit.mat[33][25] = cpu.Cell.conductor
circuit.mat[33][26] = cpu.Cell.transistor
circuit.mat[33][29] = cpu.Cell.conductor
circuit.mat[33][55] = cpu.Cell.live
circuit.mat[33][56] = cpu.Cell.conductor
circuit.mat[33][57] = cpu.Cell.conductor
circuit.mat[33][58] = cpu.Cell.conductor
circuit.mat[33][59] = cpu.Cell.conductor
circuit.mat[33][60] = cpu.Cell.conductor
circuit.mat[33][61] = cpu.Cell.conductor
circuit.mat[33][62] = cpu.Cell.conductor
circuit.mat[33][63] = cpu.Cell.conductor
circuit.mat[33][64] = cpu.Cell.conductor
circuit.mat[33][65] = cpu.Cell.conductor
circuit.mat[34][11] = cpu.Cell.conductor
circuit.mat[34][12] = cpu.Cell.conductor
circuit.mat[34][13] = cpu.Cell.conductor
circuit.mat[34][14] = cpu.Cell.conductor
circuit.mat[34][15] = cpu.Cell.conductor
circuit.mat[34][16] = cpu.Cell.conductor
circuit.mat[34][18] = cpu.Cell.conductor
circuit.mat[34][19] = cpu.Cell.conductor
circuit.mat[34][20] = cpu.Cell.conductor
circuit.mat[34][21] = cpu.Cell.transistor_gate
circuit.mat[34][23] = cpu.Cell.transistor_gate
circuit.mat[34][25] = cpu.Cell.transistor
circuit.mat[34][26] = cpu.Cell.conductor
circuit.mat[34][27] = cpu.Cell.live
circuit.mat[34][29] = cpu.Cell.ground
circuit.mat[35][13] = cpu.Cell.resistor
circuit.mat[35][18] = cpu.Cell.resistor
circuit.mat[35][21] = cpu.Cell.transistor
circuit.mat[35][22] = cpu.Cell.conductor
circuit.mat[35][23] = cpu.Cell.transistor
circuit.mat[35][24] = cpu.Cell.conductor
circuit.mat[35][25] = cpu.Cell.transistor_gate
circuit.mat[36][13] = cpu.Cell.conductor
circuit.mat[36][17] = cpu.Cell.live
circuit.mat[36][18] = cpu.Cell.conductor
circuit.mat[36][20] = cpu.Cell.live
circuit.mat[36][21] = cpu.Cell.conductor
circuit.mat[36][25] = cpu.Cell.resistor
circuit.mat[36][26] = cpu.Cell.conductor
circuit.mat[36][27] = cpu.Cell.ground
circuit.mat[37][13] = cpu.Cell.live

circuit.generate_groups()
circuit.generate_dyn_groups()
circuit.generate_res_groups()
circuit.update_transistors()

resize(res)
pres = pygame.display.list_modes()[0]
pygame.key.set_repeat(500, 50)
clock = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		mods = pygame.key.get_mods()

		if event.type == KEYDOWN:
			if   event.key == K_ESCAPE:
				if select_state is not SelectState.inactive:
					select_state = SelectState.inactive
				# else: running = False

			elif event.key == K_F11: toggleFullscreen()
			elif event.key == K_SPACE: scrolling = True

			elif event.mod & (KMOD_LCTRL|KMOD_RCTRL):
				# e for Export
				if event.key == K_e: print(end=circuit.generate_source())

			elif event.key == K_s:
				# s for Select
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					select_state = SelectState.ready
				else:
					select_state = SelectState.active
				select_mode = SelectMode.undecided

			elif event.key == K_d:
				# d for Duplicate
				if select_state is SelectState.inactive:
					if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
						select_state = SelectState.ready
					else:
						select_state = SelectState.active
				select_mode = SelectMode.copy

			elif event.key == K_f:
				# f for Fill
				if select_state is SelectState.inactive:
					if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
						select_state = SelectState.ready
					else:
						select_state = SelectState.active
				select_mode = SelectMode.fill

			elif event.key == K_c:
				# c for Conductor
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					paint_mode = cpu.Cell.insulator
				else:
					paint_mode = cpu.Cell.conductor
			elif event.key == K_v:
				# v for Voltage
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					paint_mode = cpu.Cell.ground
				else:
					paint_mode = cpu.Cell.live
			elif event.key == K_t:
				# t for Transistor
				if event.mod & (KMOD_LSHIFT|KMOD_RSHIFT):
					paint_mode = cpu.Cell.transistor_gate
				else:
					paint_mode = cpu.Cell.transistor
			elif event.key == K_r:
				# r for Resistor
				paint_mode = cpu.Cell.resistor
			elif event.key == K_2:
				# 2 because two conductors in one space
				paint_mode = cpu.Cell.overlap

			elif event.key == K_g:
				# g for Groups
				circuit.generate_groups()
				circuit.generate_dyn_groups()
				circuit.generate_res_groups()
			elif event.key == K_u:
				# u for Update
				circuit.update_transistors()

			elif event.key == K_i:
				# i for Information
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
		elif event.type == KEYUP:
			if event.key == K_SPACE: scrolling = False

		elif event.type == VIDEORESIZE:
			if not display.get_flags()&FULLSCREEN: resize(event.size)
		elif event.type == QUIT: running = False

		elif event.type == MOUSEWHEEL:
			if mods & (KMOD_LSHIFT|KMOD_RSHIFT|KMOD_LALT|KMOD_RALT): continue

			view_rect[0] += event.x * WHEEL_FAC
			view_rect[1] -= event.y * WHEEL_FAC

		elif event.type == MOUSEBUTTONDOWN:

			if event.button in (4, 5):
				if mods & (KMOD_LCTRL|KMOD_RCTRL):
					old_size = size

					if event.button == 5:
						size *= ZOOM_FAC_NUM
						size //= ZOOM_FAC_DEN
						if size < 2: size = 2
					elif event.button == 4:
						if size <= 2: size += 2
						size *= ZOOM_FAC_DEN
						size //= ZOOM_FAC_NUM

					# top_left of the rect should move proportionally
					view_rect[0] += event.pos[0]
					view_rect[0] *= size
					view_rect[0] //= old_size
					view_rect[0] -= event.pos[0]

					view_rect[1] += event.pos[1]
					view_rect[1] *= size
					view_rect[1] //= old_size
					view_rect[1] -= event.pos[1]

				elif mods & (KMOD_LSHIFT|KMOD_RSHIFT):
					delta = event.button*2-9
					view_rect[0] += delta * WHEEL_FAC

				elif mods & (KMOD_LALT|KMOD_RALT):
					delta = event.button*2-9
					val = paint_mode.value + delta - 1
					val %= len(cpu.Cell)
					val += 1
					paint_mode = cpu.Cell(val)

			elif event.button == 1:
				click_pos = from_screen_space(event.pos, view_rect, size)


				if mods & (KMOD_LALT|KMOD_RALT):
					x, y = click_pos
					paint_mode = circuit.mat[y][x]

				elif select_state is SelectState.active:
					select_region = [click_pos, click_pos]
					select_state = SelectState.selecting
				elif select_state is SelectState.ready:
					# paste
					if select_mode is SelectMode.copy:

						copy_h = select_region[1][1] - select_region[0][1] + 1
						copy_w = select_region[1][0] - select_region[0][0] + 1

						# no overlap safety.
						# The simplest type of copy will work
						for dest_row, src_row in zip(
							circuit.mat[click_pos[1]:click_pos[1] + copy_h],
							circuit.mat[select_region[0][1]:select_region[1][1]+1],
						):

							dest_row[click_pos[0]:click_pos[0] + copy_w] = (
								src_row[select_region[0][0]:select_region[1][0]+1]
							)

					elif select_mode is SelectMode.fill:

						for src_row in circuit.mat[
							select_region[0][1]:select_region[1][1]+1
						]:
							for i in range(
								select_region[0][0], select_region[1][0]+1
							):
								src_row[i] = paint_mode

					select_state = SelectState.inactive

				else:
					dragging = True
					if not pygame.key.get_mods()&(KMOD_LSHIFT|KMOD_RSHIFT):
						x, y = click_pos
						if circuit.mat[y][x] != paint_mode:
							circuit.mat[y][x] = paint_mode
							print(f'PAINTED {x, y} to {paint_mode}')

			elif event.button == 3:
				x, y = from_screen_space(event.pos, view_rect, size)
				if (x, y) in circuit.static_groups:
					selected_group = circuit.static_groups[x, y]
					if selected_group.override is not None:
						selected_group = selected_group.override
						if selected_group.resistor_override is not None:
							selected_group = selected_group.resistor_override

		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				dragging = False
				if select_state is SelectState.selecting:
					select_state = SelectState.ready
			elif event.button == 3:
				x, y = from_screen_space(event.pos, view_rect, size)
				selected_group = None
		elif event.type == MOUSEMOTION:
			if scrolling:
				view_rect[0] -= event.rel[0]
				view_rect[1] -= event.rel[1]
			elif select_state is SelectState.selecting:
				if select_region:
					select_region[1] = (
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
