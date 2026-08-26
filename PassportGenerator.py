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

import json
import math
import subprocess
from Tools import ImageTools
import geo

class PassportGenerator():
	_DEFINITIONS = {
		"adult": {
			"chin-to-head":			[ 27, 40 ],
			"chin-to-head-ideal":	[ 32, 36 ],
			"top-to-eyes":			[ 13, 23 ],
			"left-to-nose":			[ 15.5, 19.5 ]
		},
		"child": {
			"left-to-nose":			[ 15.5, 19.5 ],
			"top-to-eyes":			[ 13, 27 ],
			"chin-to-head":			[ 17, 38 ],
			"chin-to-head-ideal":	[ 22, 36 ],
		},
	}
	def __init__(self, args):
		self._args = args
		with open(self._args.json_input_filename) as f:
			self._in = json.load(f)

	def _execute(self, cmd):
		if self._args.verbose >= 3:
			print(cmd)
		subprocess.check_call(cmd)

	def _run_check(self):
		cmdline = [ "magick", self._in["image"]["filename"] ]
		print("Left eye   : %.0f, %.0f" % (self._left_eye.x, self._left_eye.y))
		print("Right eye  : %.0f, %.0f" % (self._right_eye.x, self._right_eye.y))
		print("Nose       : %.0f, %.0f" % (self._nose.x, self._nose.y))
		print("Top of head: %.0f, %.0f" % (self._top.x, self._top.y))
		print("Chin       : %.0f, %.0f" % (self._chin.x, self._chin.y))

		angle_deg = self._angle / math.pi * 180
		print("Rotation   : %.3f°" % (angle_deg))

		cmdline += ImageTools.imagemagick_draw_circle(center = self._left_eye, radius = 8, stroke = "#ffff00", fill = "none", stroke_width = 1)
		cmdline += ImageTools.imagemagick_draw_circle(center = self._right_eye, radius = 8, stroke = "#ffff00", fill = "none", stroke_width = 1)
		cmdline += ImageTools.imagemagick_draw_circle(center = self._nose, radius = 8, stroke = "#00ff00", fill = "none", stroke_width = 1)
		cmdline += ImageTools.imagemagick_draw_circle(center = self._top, radius = 8, stroke = "#ff0000", fill = "none", stroke_width = 1)
		cmdline += ImageTools.imagemagick_draw_circle(center = self._chin, radius = 8, stroke = "#ff00ff", fill = "none", stroke_width = 1)
		cmdline += ImageTools.imagemagick_draw_line(self._left_eye, self._right_eye, stroke = "#ffffff")
		cmdline += ImageTools.imagemagick_draw_line(self._top, self._chin, stroke = "#ffffff")
		cmdline += [ self._args.image_output_filename ]
		self._execute(cmdline)

	def _to_px(self, input_value, input_unit = "mm"):
		if input_unit == "mm":
			return input_value / 25.4 * self._args.resolution
		else:
			return NotImplementedError(input_unit)

	def _get_image_placements(self):
		image_count = self._dimension_canvas_mm.comp_div(1.02 * self._outlined_image_dimension_mm)
		image_count_x = math.floor(image_count.x)
		image_count_y = math.floor(image_count.y)
		if self._args.verbose >= 2:
			print("Placing %d images (%d x %d) of size %.0fmm x %.0fmm (%.0fmm x %.0fmm with border)." % (image_count_x * image_count_y, image_count_x, image_count_y, self._image_dimension_mm.x, self._image_dimension_mm.y, self._bordered_image_dimension_mm.x, self._bordered_image_dimension_mm.y))

		spacing_x = (self._dimension_canvas_mm.x - (image_count_x * self._outlined_image_dimension_mm.x)) / (image_count_x + 1)
		spacing_y = (self._dimension_canvas_mm.y - (image_count_y * self._outlined_image_dimension_mm.y)) / (image_count_y + 1)
		if self._args.verbose >= 2:
			print("Spacing in mm: X = %.1f mm Y = %.1fmm" % (spacing_x, spacing_y))

		placements_at_mm = [ ]
		for y in range(image_count_y):
			for x in range(image_count_x):
				placement = geo.Vector2d((x * self._outlined_image_dimension_mm.x) + ((x + 1) * spacing_x), (y * self._outlined_image_dimension_mm.y) + ((y + 1) * spacing_y))
				placements_at_mm.append(placement)
		return placements_at_mm

	def _compute_scale_factor(self):
		top_to_eyes_min_px = self._to_px(self._definitions["top-to-eyes"][0])
		top_to_eyes_max_px = self._to_px(self._definitions["top-to-eyes"][1])
		chin_to_head_min_px = self._to_px(self._definitions["chin-to-head"][0])
		chin_to_head_max_px = self._to_px(self._definitions["chin-to-head"][1])
		chin_to_head_ideal_px = self._to_px((self._definitions["chin-to-head-ideal"][0] + self._definitions["chin-to-head-ideal"][1]) / 2)
		chin_to_head_orig_px = (self._top - self._chin).length
		scale_min = chin_to_head_min_px / chin_to_head_orig_px
		scale_max = chin_to_head_max_px / chin_to_head_orig_px
		scale_ideal = chin_to_head_ideal_px / chin_to_head_orig_px
		if self._args.verbose >= 3:
			print("Scaling between %.3f and %.3f, ideally %.3f" % (scale_min, scale_max, scale_ideal))

		scale = scale_ideal
		if scale < scale_min:
			scale = scale_min
		elif scale > scale_max:
			scale = scale_max
		if self._args.verbose >= 2:
			print("Chosen scaling factor: %.3f" % (scale))
		return scale

	def _compute_top_to_eyes(self):
		return self._to_px((self._definitions["top-to-eyes"][0] + self._definitions["top-to-eyes"][1]) / 2)

	def _place_debug_marks(self, placement_at_mm):
		cmdline = [ ]
		image_pos = placement_at_mm + geo.Vector2d(self._args.line_size + self._args.border_size, self._args.line_size + self._args.border_size)

		# White rectangle outlining the actual image
		cmdline += ImageTools.imagemagick_draw_rectangle(geo.Box2d(base = self._to_px(image_pos), dimensions = self._to_px(self._image_dimension_mm)), stroke = "#ffffff")

		# Draw eye line
		eye_height_mm = self._definitions["top-to-eyes"][1] - self._definitions["top-to-eyes"][0]
		cmdline += ImageTools.imagemagick_draw_rectangle(geo.Box2d(base = self._to_px(image_pos + geo.Vector2d(0, self._definitions["top-to-eyes"][0])), dimensions = self._to_px(geo.Vector2d(self._image_dimension_mm.x, eye_height_mm))), fill = "#ff000040", stroke = None)

		# Draw nose line
		nose_width_mm = self._definitions["left-to-nose"][1] - self._definitions["left-to-nose"][0]
		start_at_mm = self._definitions["top-to-eyes"][0]
		cmdline += ImageTools.imagemagick_draw_rectangle(geo.Box2d(base = self._to_px(image_pos + geo.Vector2d(self._definitions["left-to-nose"][0], start_at_mm)), dimensions = self._to_px(geo.Vector2d(nose_width_mm, self._image_dimension_mm.y - start_at_mm))), fill = "#ff000040", stroke = None)

		# Draw chin and head lines
		chin = self._affine.transform(self._chin)
		top = self._affine.transform(self._top)
		space = self._to_px(1)

		# Line at chin
		cmdline += ImageTools.imagemagick_draw_relline(geo.Vector2d(self._to_px(image_pos).x, chin.y), self._to_px(geo.Vector2d(self._image_dimension_mm.x, 0)), stroke = "#ff0000")

		# Line at top of head
		cmdline += ImageTools.imagemagick_draw_relline(geo.Vector2d(self._to_px(image_pos).x, top.y), self._to_px(geo.Vector2d(self._image_dimension_mm.x, 0)), stroke = "#ff0000")

		# Horizontal arrow connecting the two
		cmdline += ImageTools.imagemagick_draw_arrow(geo.Vector2d(self._to_px(image_pos).x + space, chin.y), geo.Vector2d(self._to_px(image_pos).x + space, top.y), stroke = "#cccccc")

		size_mm = (chin.y - top.y) / self._args.resolution * 25.4
		if self._definitions["chin-to-head-ideal"][0] <= size_mm <= self._definitions["chin-to-head-ideal"][1]:
			color = "green"
			text = "OK"
		elif self._definitions["chin-to-head-ideal"][0] <= size_mm <= self._definitions["chin-to-head-ideal"][1]:
			color = "yellow"
			text = "borderline"
		else:
			color = "red"
			text = "illegal"
		cmdline += ImageTools.imagemagick_draw_text(self._to_px(image_pos + geo.Vector2d(0, -1)), "Head-to-chin: %.1f mm (%s)" % (size_mm, text), color = color, font_size = 16)

		return cmdline

	def _place_image(self, placement_at_mm):
		if self._args.verbose >= 3:
			print("Placing image at %.1fmm / %.1fmm" % (placement_at_mm[0], placement_at_mm[1]))
		cmdline = [ ]
		placement_at_px = self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._args.line_size))

		# Scale and rotate first
		self._affine = geo.TransformationMatrix.scale(self._image_scale) * geo.TransformationMatrix.rotate(self._angle)

		# Center nose horizontally
		current_nose = self._affine.transform(self._nose)
		self._affine = self._affine * geo.TransformationMatrix.translate(geo.Vector2d(-current_nose.x, 0))
		self._affine = self._affine * geo.TransformationMatrix.translate(geo.Vector2d(self._bordered_image_dimension_px.x / 2, 0))

		# Lineup eyes vertically
		current_left_eye = self._affine.transform(self._left_eye)
		self._affine = self._affine * geo.TransformationMatrix.translate(geo.Vector2d(0, -current_left_eye.y + self._image_border_px + self._top_to_eyes_px))

		# Shift by image placement
		self._affine = self._affine * geo.TransformationMatrix.translate(placement_at_px)

		cropbox = geo.Box2d(base = placement_at_px, dimensions = self._to_px(self._bordered_image_dimension_mm))
		inner_cropbox = geo.Box2d(base = placement_at_px + geo.Vector2d(self._image_border_px, self._image_border_px), dimensions = self._to_px(self._image_dimension_mm))
		cmdline += ImageTools.imagemagick_blit(self._in["image"]["filename"], self._affine, cropbox)
		return cmdline

	def _place_cutmarks(self, placement_at_mm):
		cmdline = [ ]

		# Bordered image top left
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._args.line_size)), self._to_px(geo.Vector2d(-self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._args.line_size)), self._to_px(geo.Vector2d(0, -self._args.line_size)), stroke = "#000000")

		# Bordered image bottom left
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._outlined_image_dimension_mm.y - self._args.line_size)), self._to_px(geo.Vector2d(-self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._outlined_image_dimension_mm.y - self._args.line_size)), self._to_px(geo.Vector2d(0, self._args.line_size)), stroke = "#000000")

		# Bordered image top right
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._outlined_image_dimension_mm.x - self._args.line_size, self._args.line_size)), self._to_px(geo.Vector2d(self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._outlined_image_dimension_mm.x - self._args.line_size, self._args.line_size)), self._to_px(geo.Vector2d(0, -self._args.line_size)), stroke = "#000000")

		# Bordered image bottom right
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + self._outlined_image_dimension_mm - geo.Vector2d(self._args.line_size, self._args.line_size)), self._to_px(geo.Vector2d(self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + self._outlined_image_dimension_mm - geo.Vector2d(self._args.line_size, self._args.line_size)), self._to_px(geo.Vector2d(0, self._args.line_size)), stroke = "#000000")

		# Inner image top left
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._args.line_size + self._args.border_size)), self._to_px(geo.Vector2d(-self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size + self._args.border_size, self._args.line_size)), self._to_px(geo.Vector2d(0, -self._args.line_size)), stroke = "#000000")

		# Inner image bottom left
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size, self._outlined_image_dimension_mm.y - self._args.line_size - self._args.border_size)), self._to_px(geo.Vector2d(-self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._args.line_size + self._args.border_size, self._outlined_image_dimension_mm.y - self._args.line_size)), self._to_px(geo.Vector2d(0, self._args.line_size)), stroke = "#000000")

		# Inner image top right
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._outlined_image_dimension_mm.x - self._args.line_size, self._args.line_size + self._args.border_size)), self._to_px(geo.Vector2d(self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + geo.Vector2d(self._outlined_image_dimension_mm.x - self._args.line_size - self._args.border_size, self._args.line_size)), self._to_px(geo.Vector2d(0, -self._args.line_size)), stroke = "#000000")

		# Inner image bottom right
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + self._outlined_image_dimension_mm - geo.Vector2d(self._args.line_size, self._args.line_size + self._args.border_size)), self._to_px(geo.Vector2d(self._args.line_size, 0)), stroke = "#000000")
		cmdline += ImageTools.imagemagick_draw_relline(self._to_px(placement_at_mm + self._outlined_image_dimension_mm - geo.Vector2d(self._args.line_size + self._args.border_size, self._args.line_size)), self._to_px(geo.Vector2d(0, self._args.line_size)), stroke = "#000000")

		return cmdline

	def _create_image(self):
		cmdline = [ "magick", "-size", "%.0fx%.0f" % (self._dimension_canvas_px.x, self._dimension_canvas_px.y), "xc:yellow" if self._args.check else "xc:white" ]
		text = "Target size: %.0f x %.0f mm, definitions for %s. Inner image %.0f x %.0fmm, bordered image %.0f x %.0fmm. Border size %.0f mm, cutmarks %.0fmm. %d dpi." % (self._dimension_canvas_mm.x, self._dimension_canvas_mm.y, self._args.picture_type, self._image_dimension_mm.x, self._image_dimension_mm.y, self._bordered_image_dimension_mm.x, self._bordered_image_dimension_mm.y, self._args.border_size, self._args.line_size, self._args.resolution)
		cmdline += ImageTools.imagemagick_draw_text(self._to_px(geo.Vector2d(2, 2)) + geo.Vector2d(0, 16), text, color = "#000000", font_size = 16)
		for placement_at_mm in self._get_image_placements():
			cmdline += self._place_image(placement_at_mm)
			cmdline += self._place_cutmarks(placement_at_mm)
			if self._args.check:
				cmdline += self._place_debug_marks(placement_at_mm)
		cmdline += [ self._args.image_output_filename ]
		self._execute(cmdline)

	def _compute_geometry(self):
		image_geometry = ImageTools.get_image_geometry(self._in["image"]["filename"])
		if ("geometry" in self._in["image"]) and (image_geometry != tuple(self._in["image"]["geometry"])):
			print("Warning: Image geometry have changed. Classified image is supposed to be %d x %d, but actual image has %d x %d pixels." % (self._in["image"]["geometry"][0], self._in["image"]["geometry"][1], image_geometry[0], image_geometry[1]))

		self._left_eye = geo.Vector2d(self._in["pois"]["left_eye"][0], self._in["pois"]["left_eye"][1])
		self._right_eye = geo.Vector2d(self._in["pois"]["right_eye"][0], self._in["pois"]["right_eye"][1])
		self._nose = geo.Vector2d(self._in["pois"]["nose"][0], self._in["pois"]["nose"][1])
		eye_center = (self._left_eye + self._right_eye) / 2
		up_vector = (self._left_eye - self._right_eye).perpendicular(y_flip = True).norm()

		mu = (self._in["pois"]["head_y"] - eye_center.y) / up_vector.y
		self._top = eye_center + (mu * up_vector)
		mu = (self._in["pois"]["chin_y"] - eye_center.y) / up_vector.y
		self._chin = eye_center + (mu * up_vector)
		self._angle = (self._right_eye - self._left_eye).get_angle()

		if self._args.verbose >= 2:
			print("Known geometry:")
			print("    Left eye  : %s" % (str(self._left_eye)))
			print("    Right eye : %s" % (str(self._right_eye)))
			print("    Nose      : %s" % (str(self._nose)))
			print("Computed geometry:")
			print("    Eye center: %s" % (str(eye_center)))
			print("    Top       : %s" % (str(self._top)))
			print("    Chin      : %s" % (str(self._chin)))
			print("    Rotation  : %.2f°" % (self._angle * 180 / math.pi))

		self._dimension_canvas_mm = geo.Vector2d(self._args.canvas_width, self._args.canvas_height)
		self._image_dimension_mm = geo.Vector2d(35, 45)
		self._bordered_image_dimension_mm = self._image_dimension_mm + (2 * geo.Vector2d(self._args.border_size, self._args.border_size))
		self._outlined_image_dimension_mm = self._bordered_image_dimension_mm + (2 * geo.Vector2d(self._args.line_size, self._args.line_size))
		if self._args.verbose >= 2:
			print("Dimensions in mm:")
			print("Canvas        : %s" % (str(self._dimension_canvas_mm)))
			print("Image         : %s" % (str(self._image_dimension_mm)))
			print("Bordered image: %s" % (str(self._bordered_image_dimension_mm)))
			print("Outlined image: %s" % (str(self._outlined_image_dimension_mm)))

		self._dimension_canvas_px = self._to_px(self._dimension_canvas_mm)
		self._bordered_image_dimension_px = self._to_px(self._bordered_image_dimension_mm)
		self._image_border_px = self._to_px(self._args.border_size)

		self._image_scale = self._compute_scale_factor()
		self._top_to_eyes_px = self._compute_top_to_eyes()

	def run(self):
		self._definitions = self._DEFINITIONS[self._args.picture_type]
		self._compute_geometry()
		self._create_image()
