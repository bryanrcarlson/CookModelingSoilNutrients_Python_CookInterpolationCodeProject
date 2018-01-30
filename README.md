## Purpose

Python script used as a command line utility to generate a series of inverse distance weighted maps from columns in a spatial (EASTING, NORTHING) CSV file.

## Requirements

* ArcGIS license with Spatial Analyst extension
* Python 2.7.10 32-bit

## Use

### Setup

* Create a directory to act as the working directory for ArcPy with the following:
    * | Output
    * | Input
        * 32611.prj
        * | Boundaries
            * CookEastDUwS\_Conservative\_line.shp (and associated files)
            * CWcatchment_line.shp (and associated files)
* Format spatially aware CSV files with the following:
    * Columns named "EASTING" and "NORTHING" with UTM Zone 11N (spatial reference 32611)
    * Site Id column named "SITE"
    * A single site Id value per file
    * Site id values are either: "Cook East", "Cook West"
    * Depth column named "DEPTH_CM"
    * A single depth value per file
    * Files that are processed in bulk (by specifying a directory path in the command line argument) need to have the same column names at the same column numbers starting with the "start column" (as specified as a command-line argument)

### Command-line arguments
* "-h", "--help": Help with tool

The following are required:
* "-i", "-inputpath": Absolute path to file or directory with spatial data (in csv format) to be interpolated
* "-c", "--startcol": Column number of which you wish to interporlate it and all columns to the right of it
* "-wd", "--workingdir": Absolute path to working directory for ArcPy, creates a \"temp\" and assumes an \"Output\"  and \"Input\" directory

### Examples

The following will generate a IDW map for each column after column 14 for each file in the "inputfiles" directory and attempt to combine maps using the mosaic tool if they have the same variable name and depth but differ by field id:

```bash
py interpolate.py -i "C:\\demo\\Input\\inputfiles" -c 14 -wd "C:\\demo"
```

The following will generate a IDW map for each column after column 20 in the file "mydata.csv".

```bash
py interpolate.py -i "C:\\demo\\Input\\inputfiles\\mydata.csv" -c 14 -wd "C:\\demo"
```

## License

As a work of the United States government, this project is in the public domain within the United States.

Additionally, we waive copyright and related rights in the work worldwide through the CC0 1.0 Universal public domain dedication.