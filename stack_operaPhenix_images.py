#!/usr/bin/env python3

import argparse
import os
import numpy as np
import tifffile as tiff
import re
from PIL import Image

def list_tiff_files(folder_path):
    try:
        # Get the list of filenames in the specified folder
        all_files = os.listdir(folder_path)

        # Filter only the TIFF files
        tiff_files = [filename for filename in all_files if filename.lower().endswith('.tiff') or filename.lower().endswith('.tif')]

        return tiff_files
        
    except FileNotFoundError:
        print(f"Folder not found: {folder_path}")
        return []


def separate_filenames(tiff_files):
    # Create a dictionary to store lists of filenames for each pattern
    tiff_files_dict = {}

    for filename in tiff_files:
        match = re.match(r'r(\d{2})c(\d{2})f(\d+)', filename)
        if match:
            row = match.group(1)
            column = match.group(2)
            frame = match.group(3)

            # Create a pattern key
            pattern_key = f"r{row}c{column}f{frame}"

            # Add the filename to the corresponding list in the dictionary
            if pattern_key in tiff_files_dict:
                tiff_files_dict[pattern_key].append(filename)
            else:
                tiff_files_dict[pattern_key] = [filename]
                
    return tiff_files_dict

def reshape_array(stack, channelnumber):
    img = stack
    c = channelnumber
    cz = img.shape[0]
    x = img.shape[1]
    y = img.shape[2]
    z = int(cz/c)
    shape = img.shape
    print("Image shape before reshaping: ", shape)
    img_reshaped = img.reshape(z, c, x, y)
    shape = img_reshaped.shape
    print("Image shape after reshaping: ", shape)
    return img_reshaped


def save_tiff(stack, output_folder, filename):

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the stacked image as a new TIFF
    save_path = os.path.join(output_folder, f"{prefix}{filename}{suffix}.tiff")
    tiff.imwrite(save_path, stack, dtype='uint16', imagej=True)
    print("File", f"{prefix}{filename}{suffix}.tiff", "saved.")


def stack_tiff(input_folder, output_folder, channelnumber):

    # Call a function to list all tiff files in input folder
    tiff_files = list_tiff_files(input_folder)
    
    # Call a function to separate the list of tiff files based on FOV to make a dictionary that contains
    # row-column-frame information as the key (filename) and a list of all files (channels, z's) associated with the key
    tiff_files_dict = separate_filenames(tiff_files)
        
    for filename, file_names in tiff_files_dict.items():
        print("\nStacking file: ", filename, "...")
        stack = None
        sorted_file_names = sorted(file_names)  # sorts paths alphabetically
        for file in sorted_file_names:
            file_path = os.path.join(input_folder, file)
            img = tiff.imread(file_path)
            if stack is None:
                stack = img
            else:
                stack = np.dstack((stack, img))
        # Save the stacked image as a new TIFF
        stack = np.moveaxis(stack, -1, 0)
        img_reshaped = reshape_array(stack, channelnumber)
        save_tiff(img_reshaped, output_folder, filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="stack_operaPhenix_images",
        description="Creates a simple stack of tiff files from Opera Phenix")
    
    # Add arguments
    parser.add_argument("--input", "-i",  help="Path to tiff files to be stacked", required=True)
    parser.add_argument("--output", "-o", help="Path for the output stack", required=True)
    parser.add_argument("--prefix", "-p", help="Prefix to be added to the filename", default = "")
    parser.add_argument("--suffix", "-s", help="Suffix to be added to the filename", default = "")
    parser.add_argument("--channels", "-c", type=int, help="Number of channels in the image", required=True)
    
    args = parser.parse_args()

    # Access the argument values
    input_path = args.input
    output_path = args.output
    prefix = args.prefix
    suffix = args.suffix
    channelnumber = args.channels
    
    imagestack = stack_tiff(input_path, output_path, channelnumber)
