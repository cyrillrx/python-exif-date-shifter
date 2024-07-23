import argparse
import os
from datetime import datetime, timedelta

from PIL import Image
from piexif import load as load_exif, dump as dump_exif, ExifIFD


def main():
    parser = argparse.ArgumentParser(description="Adjust EXIF dates of images by a specified time shift.")
    parser.add_argument("path", type=str, help="Path to the file or directory")
    parser.add_argument("shift", type=int, help="Time shift in hours")
    args = parser.parse_args()

    time_shift = timedelta(hours=args.shift)
    process_path(args.path, time_shift)


if __name__ == "__main__":
    main()


def process_path(path: str, time_shift: timedelta):
    if os.path.isfile(path):
        if is_image(path):
            shift_exif_datetime(path, time_shift)
    elif os.path.isdir(path):
        process_folder(path, time_shift)
    else:
        print(f"Path {path} is not a file or directory")


def process_folder(folder_path: str, time_shift: timedelta):
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if is_image(filepath):
            shift_exif_datetime(filepath, time_shift)


def shift_exif_datetime(filepath: str, time_shift: timedelta):
    print(f"EXIF adjusting data for file {filepath}")
    try:
        exif_dict = load_exif(filepath)
        shift_exif_datetimes(exif_dict, time_shift)

        exif_bytes = dump_exif(exif_dict)

        image = Image.open(filepath)
        image.save(filepath, exif=exif_bytes)

        print(f"EXIF data adjusted for {filepath}")
    except Exception as e:
        print(f"Failed to adjust EXIF data for {filepath}: {e}")


def shift_exif_datetimes(exif_dict: dict, time_shift: timedelta):
    shift_exif_time_with_key(exif_dict, ExifIFD.DateTimeOriginal, time_shift)
    shift_exif_time_with_key(exif_dict, ExifIFD.DateTimeDigitized, time_shift)


def shift_exif_time_with_key(exif_dict: dict, exif_key: int, time_shift: timedelta):
    current_datetime_str: str = exif_dict["Exif"][exif_key].decode('utf-8')
    print(f"- cur datetime: {current_datetime_str} exif key: {exif_key}")
    current_datetime = datetime.strptime(current_datetime_str, '%Y:%m:%d %H:%M:%S')

    new_datetime = current_datetime + time_shift

    new_datetime_str: str = new_datetime.strftime('%Y:%m:%d %H:%M:%S')
    print(f"- new datetime: {new_datetime_str} exif key: {exif_key}")
    exif_dict["Exif"][exif_key] = new_datetime_str.encode('utf-8')


def is_image(filepath: str):
    return filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png'))
