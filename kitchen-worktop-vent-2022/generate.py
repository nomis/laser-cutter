#!/usr/bin/env python3
# Copyright 2022  Simon Arlott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from decimal import Decimal
from svgpathtools import *
import collections
import itertools
import operator
import shapely.geometry

Point = collections.namedtuple("Point", ["x", "y"])

width = 1190
height = 60
zoom = 1.5

def drange(start, end, step):
	start = Decimal(start)
	end = Decimal(end)
	while start < end:
		yield start
		start += Decimal(step)

def point_to_complex(p):
	return float(p.x) + float(p.y) * 1j

def points_to_path(points):
	return Path(*[Line(point_to_complex(points[i]),
		point_to_complex(points[i + 1 if i + 1 < len(points) else 0])) for i in range(0, len(points))])

def rect(x, y, w, h):
	return [
		Point(x, y),
		Point(x + w, y),
		Point(x + w, y + h),
		Point(x, y + h)
	]

def rect45(x, y, w, h):
	aw = Decimal(pow(w, 2) / 2).sqrt()
	ah = Decimal(pow(h, 2) / 2).sqrt()
	return [
		Point(x + ah, y),
		Point(x + aw + ah, y + aw),
		Point(x + aw, y + aw + ah),
		Point(x, y + ah)
	]

def inside(p, x1, x2, y1, y2):
	return p.x >= x1 and p.y >= y1 and p.x <= x2 and p.y <= y2

def outside(p, x, op_x, y, op_y):
	return (1 if op_x(p.x, x) else 0) + (1 if op_y(p.y, y) else 0)

def line_intersect(area, line):
	isect = area.intersection(line)
	if isinstance(isect, shapely.geometry.Point):
		return [Point(isect.x, isect.y)]
	elif isinstance(isect, shapely.geometry.MultiPoint):
		return reversed([Point(point.x, point.y) for point in isect.geoms])
	return []

def polygon(points):
	return shapely.geometry.Polygon(points + points[0:1])

def constrain(points, x, y, w, h):
	x1 = x
	y1 = y
	x2 = x + w
	y2 = y + h
	area = None
	new_points = []

	def append_point(point):
		if point and not new_points or new_points[-1] != point:
			if point in new_points:
				return None
			new_points.append(point)

	def append_points(points):
		for point in points:
			append_point(point)

	shape = polygon(points)
	corners = filter(lambda corner: shape.contains(shapely.geometry.Point(corner[0])), [
		(Point(x1, y1), operator.lt, operator.lt),
		(Point(x2, y1), operator.gt, operator.lt),
		(Point(x2, y2), operator.gt, operator.gt),
		(Point(x1, y2), operator.lt, operator.gt)
	])

	for i, p in enumerate(points):
		if inside(p, x1, x2, y1, y2):
			append_point(p)
		else:
			prev_i = (len(points) - 1) if i == 0 else (i - 1)
			next_i = 0 if i == len(points) - 1 else (i + 1)
			contains_prev = inside(points[prev_i], x1, x2, y1, y2)
			contains_next = inside(points[next_i], x1, x2, y1, y2)
			if area is None:
				area = rect(x, y, w, h)
				area = shapely.geometry.LineString(area + area[0:1])
			prev_line = shapely.geometry.LineString([points[prev_i], p])
			next_line = shapely.geometry.LineString([p, points[next_i]])
			prev_isect = line_intersect(area, prev_line)
			next_isect = line_intersect(area, next_line)

			append_points(prev_isect)
			if prev_isect or next_isect:
				for corner, op_x, op_y in corners:
					if outside(points[i], corner.x, op_x, corner.y, op_y):
						append_point(corner)
			append_points(next_isect)

	return new_points if (len(new_points) > 2 and polygon(new_points).area >= 0.525) else None

def squares(x, y, w, h, gap, size):
	holes = []

	for r in range(y, y + h, size + gap):
		for c in range(x, x + w, size + gap):
			holes.append(rect(c, r, size, size))

	return holes

def herringbone(x, y, w, h, gap, size):
	holes = []

	rect_w = Decimal(3 * size)
	rect_h = Decimal(size)
	aw = Decimal(pow(rect_w, 2) / 2).sqrt()
	ah = Decimal(pow(rect_h, 2) / 2).sqrt()
	agap = Decimal(gap * gap / 2).sqrt()
	y_step = aw - ah + (2 * agap)
	x_step = (aw + ah) + agap + (aw + ah) / 2 + agap
	for r in drange(y - y_step, y + h, y_step):
		for c in drange(x - x_step, x + w, x_step):
			holes.append(rect45(c, r, rect_w, rect_h))
			holes.append(rect45(c + aw + agap, r + ah + agap, rect_h, rect_w))

	return holes

def generate(name, border_w, border_h, sections, gap_w, func, *args):
	overall = rect(0, 0, width, height)

	areas = []
	holes = []
	for i in range(0, sections):
		x = border_w + int(i * ((width - 2 * border_w) / sections))
		y = border_h
		w = (width - 2 * border_w) // sections - (gap_w if i < sections - 1 else 0)
		h = height - 2 * border_h

		areas.append(rect(x, y, w, h))
		holes.extend(filter(None, [constrain(path, x, y, w, h) for path in func(x, y, w, h, *args)]))

	paths = [points_to_path(path) for path in [overall] + areas + holes]

	wsvg(paths,
			colors=["black"] + ["red"] * len(areas) + ["black"] * len(holes),
			stroke_widths=[1] + [0.1] * len(areas) + [0.1] * len(holes),
			svg_attributes={
			"width": f"{width * zoom}px",
			"height": f"{height * zoom}px",
			"viewBox": f"0 0 {width} {height}",
		}, filename=f"vent-{name}.svg", openinbrowser=True)

generate("squares-1", 5, 5, 5, 5, squares, 1, 1)
generate("squares-2", 5, 5, 5, 5, squares, 1, 2)
generate("squares-3", 6, 6, 1, 0, squares, 2, 3)
generate("herringbone-1", 5, 5, 5, 5, herringbone, 1, 1)
generate("herringbone-2", 5, 5, 5, 5, herringbone, 1, 2)
generate("herringbone-3", 5, 5, 5, 5, herringbone, 2, 3)
