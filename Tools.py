#	gbpig - German Biometric Passport Image Generator
#	Copyright (C) 2021-2021 Johannes Bauer
#
#	This file is part of gbpig.
#
#	gbpig is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	gbpig is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with gbpig; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import sys
from pathlib import Path

# Resolve actual path before import geo
submodule_path = Path(__file__).parent / "submodules" / "geo"
sys.path.insert(0, str(submodule_path))

import geo
import subprocess
import json

class ImageTools():
	@classmethod
	def get_image_geometry(cls, filename):
		json_data = subprocess.check_output([ "magick", filename, "json:-" ])
		data = json.loads(json_data)
		image = data[0]["image"]
		return (image["geometry"]["width"], image["geometry"]["height"])

	@classmethod
	def imagemagick_draw_circle(cls, center, radius, stroke, fill, stroke_width = 1):
		return [ "-stroke", stroke, "-fill", fill, "-strokewidth", str(stroke_width), "-draw", "circle %f,%f %f,%f" % (center[0], center[1], center[0] + radius, center[1]) ]

	@classmethod
	def imagemagick_draw_line(cls, p1, p2, stroke, stroke_width = 1):
		return [ "-stroke", stroke, "-strokewidth", str(stroke_width), "-draw", "line %f,%f %f,%f" % (p1[0], p1[1], p2[0], p2[1]) ]

	@classmethod
	def imagemagick_draw_relline(cls, p1, rel, stroke, stroke_width = 1):
		p2 = p1 + rel
		return cls.imagemagick_draw_line(p1, p2, stroke, stroke_width)

	@classmethod
	def imagemagick_draw_arrow(cls, p1, p2, stroke, stroke_width = 1, tip_size = 8):
		direct = (p1 - p2).norm()
		perp = (p1 - p2).perpendicular().norm()
		cmd = cls.imagemagick_draw_line(p1 = p1, p2 = p2, stroke = stroke, stroke_width = stroke_width)
		cmd += cls.imagemagick_draw_relline(p1 = p1, rel = perp * tip_size - direct * tip_size, stroke = stroke, stroke_width = stroke_width)
		cmd += cls.imagemagick_draw_relline(p1 = p1, rel = perp * -tip_size - direct * tip_size, stroke = stroke, stroke_width = stroke_width)
		cmd += cls.imagemagick_draw_relline(p1 = p2, rel = perp * tip_size - direct * -tip_size, stroke = stroke, stroke_width = stroke_width)
		cmd += cls.imagemagick_draw_relline(p1 = p2, rel = perp * -tip_size - direct * -tip_size, stroke = stroke, stroke_width = stroke_width)
		return cmd

	@classmethod
	def imagemagick_draw_rectangle(cls, box, stroke, stroke_width = 1, fill = None):
		upper = box.base + box.dimensions
		return [ "-stroke", stroke or "none", "-strokewidth", str(stroke_width), "-fill", fill or "none", "-draw", "rectangle %f,%f %f,%f" % (box.base.x, box.base.y, upper.x, upper.y) ]

	@classmethod
	def imagemagick_draw_text(cls, pos, text, color = "red", font = "./FreeSans.otf", font_size = 12):
		return [ "-stroke", "none", "-fill", color, "-font", font, "-pointsize", str(font_size), "-draw", "text %f,%f '%s'" % (pos.x, pos.y, text) ]

	@classmethod
	def imagemagick_blit(cls, infile, affine, cropbox, virtual = "Transparent"):
		matrix = ",".join("%f" % (value) for value in affine.aslist)
		return [ "(", infile, "-virtual-pixel", virtual, "+distort", "AffineProjection", matrix, "-crop", "%.0fx%.0f+%.0f+%.0f" % (cropbox.dimensions.x, cropbox.dimensions.y, cropbox.base.x, cropbox.base.y), ")", "-flatten" ]
