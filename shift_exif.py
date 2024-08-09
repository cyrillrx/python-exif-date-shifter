import argparse
import os
from datetime import datetime, timedelta
from typing import List

import exiftool


def main():
    parser = argparse.ArgumentParser(description="Adjust EXIF dates of images and videos by a specified time shift.")
    parser.add_argument("path", type=str, help="Path to the file or directory")
    parser.add_argument("shift", type=int, help="Time shift in hours")
    args = parser.parse_args()

    time_shift = timedelta(hours=args.shift)
    process_path(args.path, time_shift)


def process_path(path: str, time_shift: timedelta):
    if os.path.isfile(path):
        if is_media(path):
            shift_exif_datetime(path, time_shift)
    elif os.path.isdir(path):
        process_folder(path, time_shift)
    else:
        print(f"Path {path} is not a file or directory")


def process_folder(folder_path: str, time_shift: timedelta):
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if is_media(filepath):
            shift_exif_datetime(filepath, time_shift)


def shift_exif_datetime(filepath: str, time_shift: timedelta):
    print(f"EXIF adjusting data for file {filepath}")
    try:
        with exiftool.ExifToolHelper() as tool:
            metadata = tool.get_metadata(filepath)

            new_metadata = shift_exif_datetimes(metadata, time_shift)
            if new_metadata:
                tool.execute(*[f"-{key}={value}" for key, value in new_metadata.items()], filepath)

        print(f"EXIF data adjusted for {filepath}")
    except Exception as e:
        print(f"Failed to adjust EXIF data for {filepath}: {e}")


def shift_exif_datetimes(metadata: List, time_shift: timedelta) -> dict:
    print(f"shift_exif_datetimes metadata length: {len(metadata)}")

    output_metadata = {}

    for input_metadata in metadata:
        add_if_exists(input_metadata, output_metadata, 'EXIF:DateTimeOriginal', time_shift)
        add_if_exists(input_metadata, output_metadata, 'EXIF:DateTimeDigitized', time_shift)

        add_if_exists(input_metadata, output_metadata, 'QuickTime:CreateDate', time_shift)
        add_if_exists(input_metadata, output_metadata, 'QuickTime:ModifyDate', time_shift)
        add_if_exists(input_metadata, output_metadata, 'QuickTime:TrackCreateDate', time_shift)
        add_if_exists(input_metadata, output_metadata, 'QuickTime:TrackModifyDate', time_shift)

        add_if_exists(input_metadata, output_metadata, 'EXIF:TrackCreateDate', time_shift)
        add_if_exists(input_metadata, output_metadata, 'EXIF:TrackModifyDate', time_shift)

        add_if_exists(input_metadata, output_metadata, 'EXIF:CreationTime', time_shift)
        add_if_exists(input_metadata, output_metadata, 'EXIF:CreateDate', time_shift)
        add_if_exists(input_metadata, output_metadata, 'EXIF:ModifyDate', time_shift)

        add_if_exists(input_metadata, output_metadata, 'EXIF:MediaCreateDate', time_shift)
        add_if_exists(input_metadata, output_metadata, 'EXIF:MediaModifyDate', time_shift)

    return output_metadata


def add_if_exists(input_metadata: dict, output_metadata: dict, key: str, time_shift: timedelta):
    if key in input_metadata:
        output_metadata[key] = shift_exif_time(input_metadata, key, time_shift)


def shift_exif_time(metadata: dict, key: str, time_shift: timedelta) -> str:
    current_datetime_str = metadata[key]
    print(f"- cur datetime: {current_datetime_str} - key: {key}")

    current_datetime = datetime.strptime(current_datetime_str, '%Y:%m:%d %H:%M:%S')

    new_datetime = current_datetime + time_shift

    new_datetime_str: str = new_datetime.strftime('%Y:%m:%d %H:%M:%S')
    print(f"- new datetime: {new_datetime_str}")
    return new_datetime_str


def is_media(filepath: str):
    return filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png', '.mp4', '.mov'))


if __name__ == "__main__":
    main()
