# 2d cpu simulator

import pygame

c = type('c', (), {'__matmul__': (lambda s, x: (*x.to_bytes(3, 'big'),)), '__sub__': (lambda s, x: (x&255,)*3)})()

from enum import Enum, auto

class Cell(Enum):
	# inputs
	live = auto()
	ground = auto()

	# conductor states
	conductor = auto()

	# misc
	insulator = auto()
	resistor = auto()
	overlap = auto()
	transistor_gate = auto()
	transistor = auto()

	def get_conductor_value(self):
		if self is self.__class__.live: return ConductorValue.hi
		if self is self.__class__.ground: return ConductorValue.lo

		return ConductorValue.z

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
		self.cells = set()
		# no need to store direct sources?

	def __or__(self, other):
		out = self.__class__()
		out.cells = self.cells | other.cells
		out.sources = self.sources | other.sources
		out.resistor_sources = self.resistor_sources | other.resistor_sources
		return out

	def __ior__(self, other):
		self.cells |= other.cells
		self.sources |= other.sources
		self.resistor_sources |= other.resistor_sources

		return self

	def __sub__(self, other):
		out = self.__class__()
		out.cells = self.cells - other.cells
		out.sources = self.sources - other.sources
		out.resistor_sources = self.resistor_sources - other.resistor_sources
		return out

	def get_value(self, circuit) -> ConductorValue:
		val = ConductorValue.z

		for x, y in self.sources:
			source_value = circuit.mat[y][x].get_conductor_value()

			if val is ConductorValue.z: val = source_value
			elif source_value is ConductorValue.z: pass
			# elif source_value is ConductorValue.x: val = ConductorValue.x
			elif source_value is not val: val = ConductorValue.x

		if val is not ConductorValue.z: return val

		for group in self.resistor_sources:
			print('WARNING: potential recursion at', next(iter(group.cells)))

			source_value = group.get_value()  # this may cause a recursion when there are resistors?

			if source_value is ConductorValue.z: continue
			if val is ConductorValue.x: continue

			if val is ConductorValue.z: val = source_value
			elif source_value is ConductorValue.x: val = ConductorValue.x; break
			elif source_value is not val: val = ConductorValue.mid

		return val

class Clock(Enum):
	lo = auto()
	hi = auto()

class Circuit:

	cell_colours = {
		Cell.live: c@0x71f2ff,
		Cell.ground: c-0,

		ConductorValue.hi: c--1,
		ConductorValue.lo: c@0x8b5539,
		ConductorValue.mid: c@0xd29d47,
		ConductorValue.x: c@0xc50000,
		ConductorValue.z: c@0x6c3b8f,

		Cell.conductor: c@0x6c3b8f,
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
		self.groups: dict[(int, int), WireGroup] = {}
		self.transistors = []

	def render(self, size, rect, highlighted_group = None):
		out = pygame.Surface(rect.size)
		out.fill(c@0xe0e000)

		for y, row in enumerate(self.mat):
			# 1122 1212 2112 1221 2121 2211
			#  no   yes  yes  yes  yes  no

			if y * size > rect.bottom or (y+1) * size < rect.top: continue

			for x, cell in enumerate(row):
				if x * size > rect.right or (x+1) * size < rect.left: continue

				# get the fill rect

				cell_rect = pygame.Rect(x * size, y * size, size, size)

				if (
					highlighted_group is not None
					and (x, y) in highlighted_group.cells
				):
					colour = c--1
				elif cell is Cell.conductor and (x, y) in self.groups:
					group = self.groups[x, y]
					val = group.get_value(self)
					colour = self.cell_colours.get(val, c@0xff00ff),
				else:
					colour = self.cell_colours.get(cell, c@0xff00ff),

				out.fill(colour, cell_rect.clip(rect).move(1-rect.left, 1-rect.top).inflate(-2, -2))

		return out

	# we need to be able to get the set of all cells that belong to a group
	# we need to be able to get the group given a pixel

	def generate_groups(self):
		self.groups = {}  # mapping from cells to groups
		merges = 0
		n_groups = 0

		conductors = (Cell.conductor, Cell.transistor_gate)

		for y, row in enumerate(self.mat):

			for x, cell in enumerate(row):
				if cell not in conductors: continue

				# cell is a conductor
				# simple connections for now
				# nothing through transistors (never anyways)
				# nothing with overlaps

				if x >= 0 and self.mat[y][x-1] in conductors:
					group = self.groups[x-1, y]

					# merge two groups
					if y >= 0 and self.mat[y-1][x] in conductors:
						merges += 1

						group2 = self.groups[x, y-1]
						if group is not group2:
							group |= group2
							for cell in group2.cells:
								self.groups[cell] = group

				elif y >= 0 and self.mat[y-1][x] in conductors:
					group = self.groups[x, y-1]
				else:
					n_groups += 1
					group = WireGroup()

				self.groups[x, y] = group
				print('Populated', (x, y))
				group.cells.add((x, y))

				if x > 0:
					if self.mat[y][x-1] in (Cell.live, Cell.ground):
						group.sources.add((x-1, y))
				if y > 0:
					if self.mat[y-1][x] in (Cell.live, Cell.ground):
						group.sources.add((x, y-1))

				if x < len(self.mat[0]):
					if self.mat[y][x+1] in (Cell.live, Cell.ground):
						group.sources.add((x+1, y))
				if y < len(self.mat):
					if self.mat[y+1][x] in (Cell.live, Cell.ground):
						group.sources.add((x, y+1))
					# if self.mat[y][x-1] is Cell.resistor:
					# 	group.resistor_sources.add((x, y-1))

		print(f'Generated groups. Involved {merges} merges and creation of {n_groups} groups')
		for i, group in enumerate(self.groups.values()):
			print(i, group.cells, group.sources)
