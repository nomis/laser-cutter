#!/usr/bin/env python3
# Copyright 2025  Simon Arlott
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
import sys

Point = collections.namedtuple("Point", ["x", "y"])

hole_width = Decimal(5)
hole_length = Decimal(20)
hole_gap = Decimal(30)
zoom = 2

def point_to_complex(p):
	return float(p.x) + float(p.y) * 1j

def points_to_path(points, join=True):
	if join:
		return Path(*[Line(point_to_complex(points[i]),
			point_to_complex(points[i + 1 if i + 1 < len(points) else 0])) for i in range(0, len(points))])
	else:
		return Path(*[Line(point_to_complex(points[i]),
			point_to_complex(points[i + 1])) for i in range(0, len(points) - 1)])

def rect(x, y, w, h):
	return [
		Point(x, y),
		Point(x + w, y),
		Point(x + w, y + h),
		Point(x, y + h),
	]

def generate(name, width, height):
	overall = [rect(0, 0, width, height)]

	width = Decimal(width)
	height = Decimal(height)

	holes = []
	# Top
	holes.append(rect(width / 2 - hole_length / 2, hole_gap, hole_length, hole_width))
	# Bottom
	holes.append(rect(width / 2 - hole_length / 2, height - hole_gap - hole_width, hole_length, hole_width))
	# Left
	holes.append(rect(hole_gap, height / 2 - hole_length / 2, hole_width, hole_length))
	# Right
	holes.append(rect(width - hole_gap - hole_width, height / 2 - hole_length / 2, hole_width, hole_length))

	paths = [points_to_path(path) for path in overall] + [points_to_path(path) for path in holes]

	wsvg(paths,
			colors=["green"] * len(overall) + ["red"] * len(holes),
			stroke_widths=[1] * len(overall) + [1] * len(holes),
			svg_attributes={
			"width": f"{(width + 20) * zoom}px",
			"height": f"{(height + 20) * zoom}px",
			"viewBox": f"-10 -10 {width + 20} {height + 20}",
		}, filename=f"picture-frame-{name}.svg", openinbrowser=True)

if __name__ == "__main__":
	generate("iso-a4", 210, 297)
	generate("us-letter", 219, 281)
