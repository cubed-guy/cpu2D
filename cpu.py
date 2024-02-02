# 2d cpu simulator

import pygame

c = type('c', (), {'__matmul__': (lambda s, x: (*x.to_bytes(3, 'big'),)), '__sub__': (lambda s, x: (x&255,)*3)})()

from enum import Enum, auto

class Cell(Enum):
	# inputs
	live = auto()
	ground = auto()
	clock = auto()

	# conductor states
	hi = auto()
	mid = auto()
	lo = auto()
	x = auto()
	z = auto()

	# misc
	insulator = auto()
	resistor = auto()
	overlap = auto()
	transistor_gate = auto()
	transistor = auto()

class TransistorState(Enum):
	closed = auto()
	open = auto()

class Transistor:
	def __init__(self, gate, groups):
		self.gate = gate
		self.groups = groups
		self.state = TransistorState.closed

	@classmethod
	def from_cells(cls, matrix) -> dict[(int, int): 'Transistor']:
		...

class ConductorValue(Enum):
	hi = auto()
	lo = auto()
	mid = auto()
	x = auto()
	z = auto()

class WireGroup:
	def __init__(self):
		self.sources = set()
		self.resistor_sources = set()
		# no need to store direct sources?

	def __or__(self, other):
		out = self.__class__()
		out.sources = self.sources | other.sources
		out.resistor_sources = self.resistor_sources | other.resistor_sources
		return out

	def __sub__(self, other):
		out = self.__class__()
		out.sources = self.sources - other.sources
		out.resistor_sources = self.resistor_sources - other.resistor_sources
		return out

	def get_value(self):
		val = ConductorValue.z

		for source in self.sources:
			if val is ConductorValue.z: val = source.value
			elif source.value is ConductorValue.z: pass
			elif source.value is ConductorValue.x: val = ConductorValue.x
			elif source.value is not val: val = ConductorValue.x

		if val is not ConductorValue.z: return val

		for source in self.resistor_sources:
			if source.value is ConductorValue.z: continue
			if val is ConductorValue.x: continue

			if val is ConductorValue.z: val = source.value
			elif source.value is ConductorValue.x: val = ConductorValue.x
			elif source.value is not val: val = ConductorValue.mid

		return val

class Clock(Enum):
	lo = auto()
	hi = auto()

class Circuit:
	cell_colours = {
		Cell.live: c@0x71f2ff,
		Cell.ground: c-0,
		Cell.clock: c@0x4f940b,

		Cell.hi: c--1,
		Cell.lo: c@0x8b5539,
		Cell.mid: c@0xd29d47,
		Cell.x: c@0xc50000,
		Cell.z: c@0x6c3b8f,

		Cell.insulator: c@0xfff800,
		Cell.resistor: c@0x5a5552,
		Cell.overlap: c@0x742500,
		Cell.transistor_gate: c@0xde5562,
		Cell.transistor: c@0x9ce652,
	}

	def __init__(self, w, h):
		self.w = w
		self.h = h
		self.mat: list[list[Cell]] = [[Cell.insulator]*w for _ in range(h)]
		self.clocks = []
		self.clock_state = Clock.lo
		self.groups = {}

	def render(self, size, rect):
		out = pygame.Surface(rect.size)

		for y, row in enumerate(self.mat):
			# 1122 1212 2112 1221 2121 2211
			#  no   yes  yes  yes  yes  no

			if y * size > rect.bottom or (y+1) * size < rect.top: continue
			for x, cell in enumerate(row):
				if x * size > rect.right or (x+1) * size < rect.left: continue

				# get the fill rect

				cell_rect = pygame.Rect(x * size, y * size, size, size)

				out.fill(
					self.cell_colours.get(cell, c@0xff00ff),
					cell_rect.clip(rect).move(-rect.left, -rect.top),
				)

		return out
