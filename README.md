# Adjust EXIF Datetime
This Python script adjusts the EXIF datetime of images by a specified time shift.
It can process a single file or all image files in a directory.

## Features

- Adjust EXIF datetime for individual image files.
- Process all image files in a directory and adjust their EXIF datetime.
- Supports multiple image formats: JPG, JPEG, TIFF, PNG.

## Requirements

- Python 3.x
- Pillow
- piexif

## Installation

1. Clone this repository or download the script file.
2. Install the required Python packages:

```bash
    pip install pillow piexif
```

## Usage

You can use this script from the command line.
The script takes two arguments:
the path to a file or directory, and the time shift in hours.

```bash
python shift_exif.py <path> <shift>
```

### Parameters

*`<path>`: The path to a file or directory.
*`<shift>`: The time shift in hours. 
Use a positive value to shift the time forward, and a negative value to shift it backward.

### Examples

1. Adjust the EXIF datetime of a single image file by adding 5 hours

```bash
python shift_exif.py /path/to/image.jpg 5
```

1. Adjust the EXIF datetime of all image files in a directory by subtracting 3 hours:

```bash
python shift_exif.py /path/to/directory -3
```
