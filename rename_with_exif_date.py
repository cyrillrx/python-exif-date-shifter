import argparse
import os
from datetime import datetime, timedelta
from typing import List

import exiftool

processed_files: dict = {}  # key: filepath, value: new filename
skipped_files: dict = {}  # key: filename, value: reason


def main():
    parser = argparse.ArgumentParser(description="Rename file based on EXIF dates.")
    parser.add_argument("path", type=str, help="Path to the file or directory")
    parser.add_argument("--suffix", type=str, default="none", help="keeps path as suffix if empty")
    parser.add_argument("--filter", type=str, default="", help="Processing files containing this string")
    parser.add_argument("--timeShift", type=int, default=0, help="Time shift in hours")
    parser.add_argument("--dryRun", action='store_true', help="Use to show new names without renaming")
    args = parser.parse_args()

    time_shift = timedelta(hours=args.timeShift)

    process_path(path=args.path, suffix=args.suffix, contains=args.filter, time_shift=time_shift)

    dry_run = args.dryRun

    if dry_run:
        print(f"DRY RUN: No files will be renamed")

    print(f"\nFiles renamed: {len(processed_files)}:")
    for filepath, new_filename in processed_files.items():
        if dry_run:
            print(f"DRY RUN: File would be renamed {filepath} -> {new_filename}")
        else:
            os.rename(filepath, os.path.join(os.path.dirname(filepath), new_filename))
            print(f"File renamed {filepath} -> {new_filename}")

    print(f"\nFiles skipped: {len(skipped_files)}:")
    # for key, value in skipped_files.items():
    #     print(f"{key} -> {value}")


def process_path(path: str, suffix: str, contains: str, time_shift: timedelta):
    if os.path.isfile(path):
        rename_file(path, suffix, contains, time_shift)
    elif os.path.isdir(path):
        process_folder(path, suffix, contains, time_shift)
    else:
        skipped_files[path] = "Path is not a file or directory"


def process_folder(folder_path: str, suffix: str, contains: str, time_shift: timedelta):
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        rename_file(filepath, suffix, contains, time_shift)


def rename_file(filepath: str, suffix: str, contains: str, time_shift: timedelta):
    if not is_media(filepath):
        skipped_files[filepath] = "Non-media file"
        return  # skip non-media files
    if contains != '' and contains not in filepath:
        skipped_files[filepath] = f"Does not contain filter {contains}"
        return  # skip files that do not contain the filter string

    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(filepath)

            new_filename = get_new_name(filepath, metadata, suffix, time_shift)

            if new_filename == "":
                skipped_files[filepath] = "No EXIF dates found"
                return

            processed_files[filepath] = new_filename
            print(f"File will be renamed {os.path.basename(filepath)} -> {new_filename}")

    except Exception as e:
        skipped_files[filepath] = f"Failed to read EXIF data: {e}"


def get_new_name(original_filename: str, metadata: List, suffix: str, time_shift: timedelta) -> str:
    formatted_dates = get_formatted_exif_dates(metadata, time_shift)
    basename = os.path.basename(original_filename)

    if len(formatted_dates) > 0:
        if suffix == "":
            return formatted_dates[0] + "__" + basename
        elif suffix == "none":
            return formatted_dates[0] + os.path.splitext(basename)[1].lower()
        else:
            return formatted_dates[0] + suffix + os.path.splitext(basename)[1].lower()
    else:
        return ""


def get_formatted_exif_dates(metadata: List, time_shift: timedelta, fmt: str = '%Y%m%d_%H%M%S') -> List:
    output_names = []

    for input_metadata in metadata:
        add_gps_name(input_metadata, output_names, fmt, time_shift)

        add_exif_name(input_metadata, output_names, 'EXIF:DateTimeOriginal', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'EXIF:DateTimeDigitized', fmt, time_shift)

        add_exif_name(input_metadata, output_names, 'QuickTime:CreateDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'QuickTime:ModifyDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'QuickTime:TrackCreateDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'QuickTime:TrackModifyDate', fmt, time_shift)

        add_exif_name(input_metadata, output_names, 'EXIF:TrackCreateDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'EXIF:TrackModifyDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'EXIF:CreationTime', fmt, time_shift)

        add_exif_name(input_metadata, output_names, 'EXIF:CreateDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'EXIF:ModifyDate', fmt, time_shift)

        add_exif_name(input_metadata, output_names, 'EXIF:MediaCreateDate', fmt, time_shift)
        add_exif_name(input_metadata, output_names, 'EXIF:MediaModifyDate', fmt, time_shift)

    return output_names


def add_gps_name(input_metadata: dict, output_name: List, fmt: str, time_shift: timedelta):
    gps_date_stamp_key = 'GPS:GPSDateStamp'
    gps_time_stamp_key = 'GPS:GPSTimeStamp'
    if gps_date_stamp_key in input_metadata and gps_time_stamp_key in input_metadata:
        input_datetime_str = input_metadata[gps_date_stamp_key] + " " + input_metadata[gps_time_stamp_key]
        formatted_exif_date = get_formatted_exif_date(input_datetime_str, fmt, time_shift)
        print(f"- GPS date: {formatted_exif_date}")
        output_name.append(formatted_exif_date)


def add_exif_name(input_metadata: dict, output_name: List, key: str, fmt: str, time_shift: timedelta):
    if key in input_metadata:
        input_datetime_str = input_metadata[key]
        formatted_exif_date = get_formatted_exif_date(input_datetime_str, fmt, time_shift)
        print(f"- Date: {formatted_exif_date} for key {key}")
        output_name.append(formatted_exif_date)


def get_formatted_exif_date(input_datetime_str: str, fmt: str, time_shift: timedelta) -> str:
    input_datetime = datetime.strptime(input_datetime_str, '%Y:%m:%d %H:%M:%S')
    new_datetime = input_datetime + time_shift

    output_datetime_str: str = new_datetime.strftime(fmt)
    return output_datetime_str


def is_media(filepath: str):
    return filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png', '.mp4', '.mov'))


if __name__ == "__main__":
    main()
