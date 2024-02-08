# 2d cpu simulator

import pygame
from pygame.locals import SRCALPHA, BLEND_RGBA_MULT

c = type('c', (), {'__matmul__': (lambda s, x: (*x.to_bytes(3, 'big'),)), '__sub__': (lambda s, x: (x&255,)*3)})()

from enum import Enum, auto

class Cell(Enum):
	conductor = auto()
	transistor_gate = auto()
	transistor = auto()
	resistor = auto()
	overlap = auto()

	insulator = auto()
	live = auto()
	ground = auto()

	def get_conductor_value(self):
		if self is self.__class__.live: return ConductorValue.hi
		if self is self.__class__.ground: return ConductorValue.lo

		return ConductorValue.z

conductors = (Cell.conductor, Cell.transistor_gate)
sources = (Cell.live, Cell.ground)

class ConductorValue(Enum):
	hi = auto()
	lo = auto()
	mid = auto()
	x = auto()
	z = auto()

class TransistorState(Enum):
	closed = auto()
	open = auto()

class Transistor:
	def __init__(self):
		self.gates = []
		self.groups = []
		self.state = TransistorState.closed

class Resistor:
	def __init__(self):
		self.groups: list[tuple[int, int]] = []

class WireGroup:
	id = 0

	def __init__(self):
		self.sources = set()
		self.resistors = set()
		self.transistors = set()
		self.transistor_gates = set()
		self.cells = set()
		self.id = self.id  # assign from class to obj
		self.__class__.id += 1
		self.override = None

	def __str__(self):
		rep_cell = None
		if self.cells: rep_cell = next(iter(self.cells))

		return (
			f'StaticGroup {{\n'
			f'\t{len(self.sources)} sources\n'
			f'\t{len(self.resistors)} resistors\n'
			f'\t{len(self.transistors)} transistors\n'
			f'\toverride = {self.override is not None}\n'
			f'\t{rep_cell = }\n'
			'}'
		)

	def __hash__(self):
		return self.id.__hash__()

	def __ior__(self, other):
		self.cells |= other.cells
		self.sources |= other.sources
		self.resistors |= other.resistors
		self.transistors |= other.transistors
		self.transistor_gates |= other.transistor_gates

		return self

	def get_override(self) -> 'WireGroup | DynamicWireGroup':
		if self.override is None: return self
		return self.override

	def get_resistor_override(self) -> 'WireGroup | DynamicWireGroup | ResistorWireGroup':
		if self.override is None: return self
		dyn_group = self.override
		if dyn_group.resistor_override is None: return dyn_group
		return dyn_group.resistor_override

	def is_source(self):
		return not not self.sources

	def dyn_copy(self):
		out = DynamicWireGroup()
		out.sources = self.sources.copy()
		out.resistors = self.resistors.copy()
		out.transistors = self.transistors.copy()
		out.transistor_gates = self.transistor_gates.copy()
		out.groups = {self}

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

		return val

class DynamicWireGroup:
	def __init__(self):
		self.sources = set()
		self.resistors = set()
		self.transistors = set()
		self.transistor_gates = set()
		self.groups = set()  # we need this so we can update the overrides
		self.resistor_override = None


	def __str__(self):
		rep_cell = None
		for group in self.groups:
			if group.cells:
				rep_cell = next(iter(group.cells))
				break

		return (
			f'DynamicGroup {{\n'
			f'\t{len(self.sources)} sources\n'
			f'\t{len(self.resistors)} resistors\n'
			f'\t{len(self.transistors)} transistors\n'
			f'\toverride = {self.resistor_override is not None}\n'
			f'\t{rep_cell = }\n'
			f'\tsource = {self.is_source()}\n'
			'}'
		)

	def __hash__(self):
		# if a == b then hash(a) == hash(b)
		# if hash(a) == hash(b) then a and b may or may not be equal
		return id(self).__hash__()

	# def __or__(self, other):
	# 	out = self.__class__()
	# 	out.groups = self.groups | other.groups
	# 	out.sources = self.sources | other.sources
	# 	out.resistors = self.resistors | other.resistors
	# 	return out

	def __ior__(self, other):
		self.groups |= other.groups
		self.sources |= other.sources
		self.resistors |= other.resistors
		self.transistors |= other.transistors
		self.transistor_gates |= other.transistor_gates

		return self

	def merge_static(self, static_group):
		print('Merging with the static group:', static_group)

		self.groups.add(static_group)
		self.sources |= static_group.sources
		self.resistors |= static_group.resistors
		self.transistors |= static_group.transistors
		self.transistor_gates |= static_group.transistor_gates

	def is_source(self):
		return not not self.sources

	def get_value(self, circuit) -> ConductorValue:
		val = ConductorValue.z

		for x, y in self.sources:
			source_value = circuit.mat[y][x].get_conductor_value()

			if val is ConductorValue.z: val = source_value
			elif source_value is ConductorValue.z: pass
			# elif source_value is ConductorValue.x: val = ConductorValue.x
			elif source_value is not val: val = ConductorValue.x

		if val is not ConductorValue.z: return val

		return val


class ResistorWireGroup:
	def __init__(self):
		self.sources = set()
		self.dynamic_groups = set()
		self.transistors = set()
		self.transistor_gates = set()

	def __str__(self):
		rep_cell = None
		for dynamic_group in self.dynamic_groups:
			if dynamic_group.groups:
				for group in dynamic_group.groups:
					if group.cells:
						rep_cell = next(iter(group.cells))
						break
				else: continue
				break

		return (
			f'ResistorGroup {{\n'
			f'\t{len(self.sources)} sources\n'
			f'\t{len(self.transistors)} transistors\n'
			f'\t{rep_cell = }\n'
			'}'
		)

	def __hash__(self):
		# if a == b then hash(a) == hash(b)
		# if hash(a) == hash(b) then a and b may or may not be equal
		return id(self).__hash__()

	# def __or__(self, other):
	# 	out = self.__class__()
	# 	out.groups = self.groups | other.groups
	# 	out.sources = self.sources | other.sources
	# 	out.resistors = self.resistors | other.resistors
	# 	return out

	def __ior__(self, other):
		self.sources |= other.sources
		self.dynamic_groups |= other.dynamic_groups
		self.transistors |= other.transistors
		self.transistor_gates |= other.transistor_gates

		return self

	def subtract_dyn(self, dyn_group, circuit):
		self.dynamic_groups.remove(dyn_group)

		self.update_source_groups(circuit)

		return self

	def update_source_groups(self, circuit):
		'''
		given the dynamic groups that comprise the resistor group
		return the set of all groups that are connected to sources
		'''

		self.sources.clear()

		# we assume that the dyn_group has no sources connected to it
		for dyn_group in self.dynamic_groups:
			for resistor_pos in dyn_group.resistors:
				resisitor = circuit.resistors[resistor_pos]
				for group in resistor.groups:
					group = group.get_override()
					if group.is_source():
						self.sources.add(group)

	def merge_static(self, static_group):
		print('Merging with the static group:', static_group)

		dyn_group = static_group.dyn_copy()
		static_group.override = dyn_group

		self.merge_dynamic(dyn_group)

	def merge_dynamic(self, dyn_group):
		'''
		Merges all sets EXCEPT SOURCES
		'''

		# print('Merging with the dynamic group:', dyn_group)

		self.dynamic_groups.add(dyn_group)
		self.transistors |= dyn_group.transistors
		self.transistor_gates |= dyn_group.transistor_gates

	def get_value(self, circuit) -> ConductorValue:
		val = ConductorValue.z

		for group in self.sources:
			# print('Getting source values!')

			# group = group.get_override()

			source_value = group.get_value(circuit)

			if source_value is ConductorValue.z: continue
			if val is ConductorValue.x: continue

			if val is ConductorValue.z: val = source_value
			elif source_value is ConductorValue.x: val = ConductorValue.x; break
			elif source_value is not val: val = ConductorValue.mid

		return val

class Clock(Enum):
	lo = auto()
	hi = auto()

class ActiveGate: ...

class Circuit:
	def __init__(self, w, h):
		self.w = w
		self.h = h
		self.mat: list[list[Cell]] = [[Cell.insulator]*w for _ in range(h)]
		self.static_groups: dict[(int, int), WireGroup] = {}  # separated by everything
		self.transistors: dict[(int, int), Transistor] = {}
		self.resistors: dict[(int, int), Resistors] = {}

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
		Cell.transistor: c@0x608f33,

		ActiveGate: c@0xff9ec9,

		TransistorState.open: c@0x9ce652,
		TransistorState.closed: c@0x608f33,
	}

	def render(
		self, size, rect, highlighted_group = None, *, selected_region = None
	):
		out = pygame.Surface(rect.size, SRCALPHA)
		out.fill(c@0xffe800)

		for y, row in enumerate(self.mat):
			# 1122 1212 2112 1221 2121 2211
			#  no   yes  yes  yes  yes  no

			if y * size > rect.bottom or (y+1) * size < rect.top: continue

			for x, cell in enumerate(row):
				if x * size > rect.right or (x+1) * size < rect.left: continue

				# get the fill rect

				cell_rect = pygame.Rect(x * size, y * size, size, size)

				if cell is Cell.conductor and (x, y) in self.static_groups:
					group = self.static_groups[x, y].get_resistor_override()

					if group is highlighted_group:
						if isinstance(group, ResistorWireGroup): colour = c-192
						elif isinstance(group, DynamicWireGroup): colour = c@0xffae29
						else: colour = c@0xf6ddb5
					else:
						val = group.get_value(self)
						colour = self.cell_colours.get(val, c@0xff00ff),
				elif cell is Cell.transistor_gate and (x, y) in self.static_groups:
					group = self.static_groups[x, y].get_resistor_override()

					if group is highlighted_group:
						if isinstance(group, ResistorWireGroup): colour = c-150
						elif isinstance(group, DynamicWireGroup): colour = c@0xc0ae29
						else: colour = c@0xc6ad75
					else:
						val = group.get_value(self)
						if val is ConductorValue.hi:
							colour = self.cell_colours[ActiveGate]
						else:
							colour = self.cell_colours[cell]
				elif cell is Cell.transistor and (x, y) in self.transistors:
					state = self.transistors[x, y].state
					colour = self.cell_colours.get(state, c@0xff00ff),
				else:
					colour = self.cell_colours.get(cell, c@0xff00ff),

				fill_rect = (
					cell_rect
					.clip(rect)
					.move(1-rect.left, 1-rect.top)
					.inflate(-1, -1)
				)

				out.fill(colour, fill_rect)

				if selected_region is not None:
					if x in range(
						selected_region[0][0], selected_region[1][0] + 1
					):
						if y in range(
							selected_region[0][1], selected_region[1][1] + 1
						):
							out.fill(c-225, fill_rect, special_flags=BLEND_RGBA_MULT)

		return out

	# we need to be able to get the set of all cells that belong to a group
	# we need to be able to get the group given a pixel

	def update_group_data(self, cell, group, x, y):
		ncell = self.mat[y][x]

		if ncell in sources:
			group.sources.add((x, y))
		elif ncell is Cell.transistor:
			if cell is Cell.transistor_gate:
				group.transistor_gates.add((x, y))
			else:
				group.transistors.add((x, y))
		elif ncell is Cell.resistor:
			group.resistors.add((x, y))

	def update_resistor_groups(self):
		# print('\nUPDATING RESISTOR GROUPS')

		dyn_groups: set[DynamicWireGroup] = set()

		for static_group in self.static_groups.values():
			if static_group.override is None:
				dyn_group = static_group.dyn_copy()
				static_group.override = dyn_group
			else:
				dyn_group = static_group.override
				dyn_group.override = None

			dyn_groups.add(dyn_group)

		# there are no resistor groups anymore

		queue = [*dyn_groups]

		while queue:
			dyn_group = queue.pop(0)

			if dyn_group.resistor_override is not None: continue
			if dyn_group.is_source(): continue

			res_group = None   # the resistor group that this will belong to
			sources = set()

			# print('Rippling from', dyn_group)

			for resistor_pos in dyn_group.resistors:
				# print('Looking at resistor:', resistor_pos)

				resistor = self.resistors[resistor_pos]

				# print('Connected_groups:', *resistor.groups,
				# 	sep = '\n', end='\n\n')

				for group_pos in resistor.groups:
					other_dyn_group = self.static_groups[group_pos].override
					# print('Looking at a neighbour:', other_dyn_group)

					# ripple combine resistor groups
					if other_dyn_group.resistor_override is None:
						if other_dyn_group.is_source():
							sources.add(other_dyn_group)
						else:
							queue.append(other_dyn_group)
					elif res_group is None:
						res_group = other_dyn_group.resistor_override
						res_group.merge_dynamic(dyn_group)
						dyn_group.resistor_override = res_group

					else:
						other_res_group = other_dyn_group.resistor_override
						res_group |= other_res_group
						for res_dyn_group in other_res_group.dynamic_groups:
							res_dyn_group.resistor_override = res_group

			if res_group is None:
				# print('New res_group')
				res_group = ResistorWireGroup()
				res_group.merge_dynamic(dyn_group)
				dyn_group.resistor_override = res_group

			res_group.sources |= sources
			# print('Updated sources of a res_group:', res_group)


	def generate_groups(self):
		print('GENERATING GROUPS')
		self.static_groups = {}  # mapping from cells to groups
		self.transistors = {}  # mapping from cells to groups
		merges = 0
		n_groups = 0

		for y, row in enumerate(self.mat):
			for x, cell in enumerate(row):
				if cell in conductors:

					# cell is a conductor
					# simple connections for now
					# nothing through transistors (never anyways)
					# nothing with overlaps

					if x >= 0 and self.mat[y][x-1] in conductors:
						group = self.static_groups[x-1, y]

						# merge two groups
						if y >= 0 and self.mat[y-1][x] in conductors:
							merges += 1

							group2 = self.static_groups[x, y-1]
							if group is not group2:
								group |= group2
								for cell in group2.cells:
									self.static_groups[cell] = group

					elif y >= 0 and self.mat[y-1][x] in conductors:
						group = self.static_groups[x, y-1]
					else:
						n_groups += 1
						group = WireGroup()

					self.static_groups[x, y] = group
					# print('Populated', (x, y))
					group.cells.add((x, y))

					if x > 0: self.update_group_data(cell, group, x-1, y)
					if y > 0: self.update_group_data(cell, group, x, y-1)
					if x < len(self.mat[0]): self.update_group_data(cell, group, x+1, y)
					if y < len(self.mat): self.update_group_data(cell, group, x, y+1)

				elif cell is Cell.resistor:

					resistor = Resistor()
					self.resistors[x, y] = resistor

					if x > 0 and self.mat[y][x-1] in conductors:
						resistor.groups.append((x-1, y))
					if y > 0 and self.mat[y-1][x] in conductors:
						resistor.groups.append((x, y-1))
					if x < len(self.mat[0]) and self.mat[y][x+1] in conductors:
						resistor.groups.append((x+1, y))
					if y < len(self.mat) and self.mat[y+1][x] in conductors:
						resistor.groups.append((x, y+1))

					print('NEW RESISTOR AT', (x, y), resistor.groups)

				elif cell is Cell.transistor:
					transistor = Transistor()
					self.transistors[x, y] = transistor

					if x > 0:
						if self.mat[y][x-1] is Cell.conductor:
							transistor.groups.append((x-1, y))
						elif self.mat[y][x-1] is Cell.transistor_gate:
							transistor.gates.append((x-1, y))
					if y > 0:
						if self.mat[y-1][x] is Cell.conductor:
							transistor.groups.append((x, y-1))
						elif self.mat[y-1][x] is Cell.transistor_gate:
							transistor.gates.append((x, y-1))

					if x < len(self.mat[0]):
						if self.mat[y][x+1] is Cell.conductor:
							transistor.groups.append((x+1, y))
						elif self.mat[y][x+1] is Cell.transistor_gate:
							transistor.gates.append((x+1, y))
					if y < len(self.mat):
						if self.mat[y+1][x] is Cell.conductor:
							transistor.groups.append((x, y+1))
						elif self.mat[y+1][x] is Cell.transistor_gate:
							transistor.gates.append((x, y+1))

		# print(f'Generated groups. Involved {merges} merges and creation of {n_groups} groups')
		# for i, group in enumerate(self.static_groups.values()):
		# 	print(i, group.cells, group.sources)

	def update_transistors(self):
		print('UPDATING TRANSISTORS')
		# a transistor is dormant for the rest of the tick
		# if it already changed its value in this tick
		dormants = set()
		queue = [*self.transistors]

		while queue:
			# print('Update Transistor queue', queue)
			transistor_pos = queue.pop(0)

			if transistor_pos in dormants: continue  # don't update

			transistor = self.transistors[transistor_pos]

			for pos in transistor.gates:
				group = self.static_groups[pos].get_resistor_override()

				if group.get_value(self) is ConductorValue.hi:
					new_state = TransistorState.open
					break

			else:
				new_state = TransistorState.closed

			if transistor.state is new_state: continue

			transistor.state = new_state
			dormants.add(transistor_pos)

			# transistor update code won't be in transistor
			# it'll be here.

			if new_state is TransistorState.open:
				# merge groups
				merged = DynamicWireGroup()

				'''
				After the dynamic groups have been merges,
				we must attend to the resistor groups.
				'''

				resistor_merged = ResistorWireGroup()

				for pos in transistor.groups:
					group = self.static_groups[pos]
					if group.override is not None:
						# self.dynamic_groups.remove(group.override)
						dyn_group = group.override

						merged |= dyn_group

						# TODO: merge resistor groups
						if resistor_merged is None: continue

						if dyn_group.is_source():
							# At least one sourced group. This means no resistor group.
							resistor_merged = None  # subtract later
						elif dyn_group.resistor_override is not None:
							# Sources also get merged here. Good
							resistor_merged |= dyn_group.resistor_override
						else:
							resistor_merged.merge_dynamic(dyn_group)

					else:
						merged.merge_static(group)

						if resistor_merged is None: continue
						if group.is_source():
							resistor_merged = None
						else:
							resistor_merged.merge_static(group)

				for static_group in merged.groups:
					static_group.override = merged

				if resistor_merged is None:
					# iterate through each group and subtract merged
					# then update the sources, because subtraction won't be that simple
					# as in, simply subtracting the sources won't suffice

					for resistor_pos in merged.resistors:
						resistor = self.resistors[resistor_pos]
						print(f'resistor at {resistor_pos} = Resistor({resistor.groups})')
						for outer_group_pos in resistor.groups:
							# for every static group connected through
							# a resistor from this source group

							# Conductors are at these spots: (12, 5) (20, 5) (12, 6) (20, 6) (12, 7) (18, 7) (20, 7) (11, 8) (13, 8) (19, 8) (21, 8) (11, 9) (19, 9) (22, 9) (12, 10) (13, 10) (18, 10) (20, 10) (21, 10) (11, 11) (19, 11) (22, 11) (11, 12) (19, 12) (11, 13) (19, 13)
							# print('Conductors are at these spots:', *self.static_groups)
							outer_group = self.static_groups[outer_group_pos]
							dyn_outer_group = outer_group.get_override()
							if dyn_outer_group.is_source(): continue

							# Finds all the dynamic_groups that are connected
							# through resistors and open transistors.
							# Stops ripple if it finds a source.
							# Adds that to sources instead.
							resistor_group = self.find_res(dyn_outer_group)

							for dynamic_group in resistor_group.dynamic_groups:
								dynamic_group.resistor_override = resistor_group
								for static_group in dynamic_group.static_groups:
									static_group.override = dynamic_group

						# find the sources? that'll be handled by find_res()

					for updated_transistor in merged.transistor_gates:
						queue.append(updated_transistor)

				else:
					for updated_transistor in resistor_merged.transistors:
						queue.append(updated_transistor)
					# iterate through all the dynamic_groups that may have been affected?
					# which dyn_group would change if only the res_group changed? None

				merged.resistor_override = resistor_merged

			elif new_state is TransistorState.closed:
				# disconnection logic
				for pos in transistor.groups:
					print('New disconnected group')
					group = self.static_groups[pos]
					dyn_group = self.find_dyn(group)

					# FIX: wasted effort if same group connected

					for static_group in dyn_group.groups:
						if static_group.override is not None:
							static_group.override

						static_group.override = dyn_group

					for updated_transistor in dyn_group.transistor_gates:
						queue.append(updated_transistor)

			else:
				raise ValueError(f'Invalid transistor state: {new_state!r}')

		# TODO: This should not be necessary. It updated EVERYTHING.
		# self.update_resistor_groups()

	def find_dyn(self, root_group: WireGroup):
		out = DynamicWireGroup()

		queue = [root_group]
		while queue:
			group = queue.pop(0)
			if group in out.groups: continue  # already merged

			out.merge_static(group)
			# group.override = out
			print('Adding to disconnected dynamic group:', group.cells)
			print('Dynamic group now has transistors at:', out.transistors)
			print('Static group now has transistors at:', group.transistors)

			for transistor_pos in group.transistors:
				print('Getting groups linked to transistor at', transistor_pos)

				transistor = self.transistors[transistor_pos]

				if transistor.state is TransistorState.closed: continue

				for ripple_group_pos in transistor.groups:
					ripple_group = self.static_groups[ripple_group_pos]
					if ripple_group is not group:
						queue.append(ripple_group)

		return out

	def find_res(self, root_group: DynamicWireGroup) -> ResistorWireGroup:
		out = ResistorWireGroup()

		queue = [root_group]
		while queue:
			dyn_group = queue.pop(0)
			if dyn_group in out.dynamic_groups: continue  # already merged

			if dyn_group.is_source():
				# don't ripple from a source group
				out.sources.add(dyn_group)
				continue

			out.merge_dynamic(dyn_group)
			# dyn_group.resistor_override = out
			print('Adding to disconnected resistor group:', dyn_group.cells)
			print('Resistor group now has resistors at:', out.resistors)
			print('Dynamic group now has resistors at:', dyn_group.resistors)

			for resistor_pos in dyn_group.resistors:
				print('Getting groups linked to resistor at', resistor_pos)

				resistor = self.resistors[resistor_pos]

				for ripple_group_pos in transistor.groups:
					ripple_group = self.static_groups[ripple_group_pos]
					if ripple_group is not dyn_group:
						queue.append(ripple_group)

		return out

	def find_resistor_group(self, root_group: DynamicWireGroup) -> ResistorWireGroup:
		# similar but not the same as find_dyn()
		...


	import io
	def generate_source(self):
		out = self.io.StringIO()
		for y, row in enumerate(self.mat):
			for x, cell in enumerate(row):
				if cell is Cell.insulator: continue
				print(f'circuit.mat[{y}][{x}] = {cell}', file=out)

		return out.getvalue()

if __name__ == '__main__': import main
