#!/usr/bin/env python3

from svgpathtools import *
import itertools

width = 1190
height = 60
zoom = 1.5

def c(x, y):
	return x + y * 1j

def rect(x, y, w, h):
	return Path(
		Line(c(x, y), c(x + w, y)),
		Line(c(x + w, y), c(x + w, y + h)),
		Line(c(x + w, y + h), c(x, y + h)),
		Line(c(x, y + h), c(x, y))
	)

def squares(x, y, w, h, gap, size):
	holes = []

	for r in range(y, y + h, size + gap):
		hh = size
		while r + hh > y + h:
			hh -= 1
		if hh < 1:
			continue
		for c in range(x, x + w, size + gap):
			hw = size
			while c + hw > x + w:
				hw -= 1
			if hw < 1:
				continue
			holes.append(rect(c, r, hw, hh))

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
		holes.extend(func(x, y, w, h, *args))

	paths = [overall] + areas + holes

	wsvg(paths,
			colors=["black"] + ["red"] * len(areas) + ["green"] * len(holes),
			stroke_widths=[1] + [0.5] * len(areas) + [0.1] * len(holes),
			svg_attributes={
			"width": f"{width * zoom}px",
			"height": f"{height * zoom}px",
			"viewBox": f"0 0 {width} {height}",
		}, filename=f"vent-{name}.svg", openinbrowser=True)

generate("squares-1", 5, 5, 5, 5, squares, 1, 1)
generate("squares-2", 5, 5, 5, 5, squares, 1, 2)
generate("squares-3", 6, 6, 1, 0, squares, 2, 3)
