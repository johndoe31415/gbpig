# gbpig
gbpig is the German Biometric Passport Image Generator. It was originally some
GIMP templates, but is now a Python script that takes any image along with the
following metadata in JSON format:

  * Y-coordinate of the chin
  * Y-coordinate of the top of head
  * Coordinate of the left eye
  * Coordinate of the right eye
  * Coordinate of tip of nose

These, along with the source image, are fed into the script which generates a
printable version.

It has been generated from a template that was created from the orginal
Bundesdruckerei PDFs and that works for both adults and children under the age
of 10. Original documentation can be found here:

  * [For adults](https://www.bmi.bund.de/SharedDocs/downloads/DE/veroeffentlichungen/themen/moderne-verwaltung/ausweise/passbild-schablone-erwachsene.pdf)
  * [For children](https://www.bmi.bund.de/SharedDocs/downloads/DE/veroeffentlichungen/themen/moderne-verwaltung/ausweise/passbild-schablone-kinder.pdf)

## Usage
Create the JSON file:

```json
{
    "image": {
        "filename": "my_pretty_image.jpg"
    },
    "pois": {
        "chin_y": 2123,
        "head_y": 773,
        "left_eye": [ 3086, 1436 ],
        "right_eye": [ 3428, 1431 ],
		"nose": [ 3268, 1683 ]

    }
}
```

And then:

```
$ ./generate_image image.json print_me.jpg
```

If you want to use the parameters for children, do:

```
$ ./generate_image -t child image.json print_me.jpg
```

All parameters are shown on the help page:

```
$ ./generate_image --help
usage: generate_image [-h] [-r dpi] [-t {adult,child}] [-b mm] [-l mm] [-W mm]
                      [-H mm] [-c] [-v]
                      json_input_filename image_output_filename

Generate a biometric passport photo.

positional arguments:
  json_input_filename   JSON file which describes the source image along with
                        points of interest (POIs) in pixel coordinates.
  image_output_filename
                        Output image file.

optional arguments:
  -h, --help            show this help message and exit
  -r dpi, --resolution dpi
                        Output image resolution in dpi. Defaults to 300 dpi.
  -t {adult,child}, --picture-type {adult,child}
                        Give the picture type. Can be any of adult, child,
                        defaults to adult.
  -b mm, --border-size mm
                        Specifies the dimension around the image that is
                        included (in mm). Defaults to 5.0 mm.
  -l mm, --line-size mm
                        Specifies the length of cutting lines in mm. Defaults
                        to 2.0 mm.
  -W mm, --canvas-width mm
                        Specifies the output canvas width in mm. Defaults to
                        100.0 mm.
  -H mm, --canvas-height mm
                        Specifies the output canvas height in mm. Defaults to
                        150.0 mm.
  -c, --check           Allows you to check the classification was correct by
                        creating additional help lines.
  -v, --verbose         Increases verbosity. Can be specified multiple times
                        to increase.
```

## License
GNU GPL-3.
