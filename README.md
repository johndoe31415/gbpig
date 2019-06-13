# German Biometric Passport Image
This is a template that was created from the orginal Bundesdruckerei PDFs and
that works for both adults and children under the age of 10. Original
documentation can be found here:

  * [For adults](https://www.bmi.bund.de/SharedDocs/downloads/DE/veroeffentlichungen/themen/moderne-verwaltung/ausweise/passbild-schablone-erwachsene.pdf)
  * [For children](https://www.bmi.bund.de/SharedDocs/downloads/DE/veroeffentlichungen/themen/moderne-verwaltung/ausweise/passbild-schablone-kinder.pdf)

## Usage
1. Open the template.xcf image in the GIMP.
2. Paste photograph as new layer as child of A -> Bild/A. The layer mask
   ensures it is correctly clipped.
3. Enable layers for either child or adult (by default, adult is active).
4. Align nose and eyes with layers.
5. Show chin and head layer. Move chin/head layer so that the red line stops at
   the chin.
6. Now resize image that end of head stays within the green/yellow head area
   (green is ideal, yellow is permissible).
7. Repeat with B, C, D as you like. If you want to keep the exact alignment
   that you already had in A, do as follows:
   1. Right click A -> Bild/A and do "Merge Layer Group", then do "Apply layer
	  mask".
   2. Layer -> Crop to Content.
   3. Edit -> Copy (Ctrl-C).
   4. Change active layer to destination layer placeholder, e.g., B -> Bild/B -> Placeholder #1.
   5. Edit -> Paste (Ctrl-V).
   6. Layer -> Anchor Layer (Ctrl-H).
8. Print out as a 10x15 picture.

## License
CC-BY-SA 3.0.
