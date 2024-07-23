import os
from datetime import datetime, timedelta

from PIL import Image
from piexif import load as load_exif, dump as dump_exif, ExifIFD


def adjust_photo_exif(filepath: str, time_shift: timedelta):
    print(f"EXIF adjusting data for file {filepath}")
    try:
        exif_dict = load_exif(filepath)
        shift_exif_times(exif_dict, time_shift)

        exif_bytes = dump_exif(exif_dict)

        image = Image.open(filepath)
        image.save(filepath, exif=exif_bytes)

        print(f"EXIF data adjusted for {filepath}")
    except Exception as e:
        print(f"Failed to adjust EXIF data for {filepath}: {e}")


def shift_exif_times(exif_dict: dict, time_shift: timedelta):
    shift_exif_time(exif_dict, ExifIFD.DateTimeOriginal, time_shift)
    shift_exif_time(exif_dict, ExifIFD.DateTimeDigitized, time_shift)


def shift_exif_time(exif_dict: dict, exif_key: int, time_shift: timedelta):
    current_datetime_str: str = exif_dict["Exif"][exif_key].decode('utf-8')
    print(f"- cur datetime: {current_datetime_str} exif key: {exif_key}")
    current_datetime = datetime.strptime(current_datetime_str, '%Y:%m:%d %H:%M:%S')

    new_datetime = current_datetime + time_shift

    new_datetime_str: str = new_datetime.strftime('%Y:%m:%d %H:%M:%S')
    print(f"- new datetime: {new_datetime_str} exif key: {exif_key}")
    exif_dict["Exif"][exif_key] = new_datetime_str.encode('utf-8')


def is_image(filepath: str):
    return filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png'))


conf_time_shift = timedelta(hours=5)
conf_folder_path = "path/to/folder"

for filename in os.listdir(conf_folder_path):
    filepath = os.path.join(conf_folder_path, filename)
    if is_image(filepath):
        adjust_photo_exif(filepath, conf_time_shift)
