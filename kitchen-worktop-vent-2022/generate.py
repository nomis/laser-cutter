#!/usr/bin/env python3

from svgpathtools import *

width = 1180
height = 50
zoom = 1.5
border = 5
sections = 5

def c(x, y):
	return x + y * 1j

def rect(x, y, w, h):
	return Path(
		Line(c(x, y), c(x + w, y)),
		Line(c(x + w, y), c(x + w, y + h)),
		Line(c(x + w, y + h), c(x, y + h)),
		Line(c(x, y + h), c(x, y))
	)

overall = rect(0, 0, width, height)

areas = []
for i in range(0, sections):
	areas.append(
		rect(
			border + int(i * ((width - border) / sections)),
			border,
			(width - border) // sections - border,
			height - 2 * border
		)
	)

holes = []

paths = [overall] + areas + holes

wsvg(paths,
		colors=["black"] + ["red"] * len(areas) + ["green"] * len(holes),
		stroke_widths=[1] * len(paths),
		svg_attributes={
		"width": f"{width * zoom}px",
		"height": f"{height * zoom}px",
		"viewBox": f"0 0 {width} {height}",
	}, filename="vent.svg", openinbrowser=True)
