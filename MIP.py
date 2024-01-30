#!/usr/bin/env python3

import argparse
import os
import numpy as np
import sys
import tifffile as tiff

def read_tif(file, read_path):
    img_array = tiff.imread(os.path.join(read_path, file), is_ome=False) # originally I had "multifile=False" argument, but it generated an error)
    return img_array


def mip_tif(img_array, channelnumber):

    shape = img_array.shape
    mip_img_array= []
    
    if len(shape) == 3:
        # If the shape of the array is 3D, divide first dimension (Z+C) to create 4D array
        c = channelnumber
        cz = img_array.shape[0]
        x = img_array.shape[1]
        y = img_array.shape[2]
        z = int(cz/c)
        print("Reshaping", file, shape)
        img_array = img_array.reshape(z, c, x, y)
        shape = img_array.shape
        print(file, "shape after reshaping: ", shape)
        print(img_array.shape)
        stack_mip(img_array)

    elif len(shape) == 4:
        for channel in range(shape[1]):
            # Perform Maximum Intensity Projection along the Z-axis; does result in duplicate dimension - need to be corrected somehow
            mip_image = np.amax(img_array, axis=0)
            mip_img_array.append(mip_image)
           
    elif len(shape) == 5:
        for timepoint in range(shape[0]):
            for channel in range(shape[2]):
                mip_image = np.amax(img_array, axis=1)
                mip_img_array.append(mip_image)
    
    else:
        print("Exiting... Stack dimension something else than 3D, 4D or 5D. Check your tiff stack.")
        sys.exit()
        
    mip_img_array = np.stack(mip_img_array)
    print(mip_img_array.shape)
    return mip_img_array


        

def save_tif(img_array, file, output_folder, suffix):

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Set the save path and filename
    file = os.path.splitext(os.path.basename(file))[0]
    save_path = os.path.join(output_folder, f"{file}{suffix}.tiff")
    # Remove all axes with dimension 1 from the array
    img_array = np.squeeze(img_array)
    
    # Save the stacked image as a new TIFF
    
    
    # add a way to save in 8 bit format, since the 255 normalization
    # add to split z into z and t
    tiff.imwrite(save_path, img_array, imagej=True)
    print("File", f"{file}{suffix}.tiff", "saved.")
    

if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(
        prog="stack_timepoints.py",
        description="Stacks 4D tiff images (reshapes 3D to 4D if not reshaped before) into 5D adding timepoints, then aligns the stacks using phase cross correlation on beads channel 2.")
    
    # Add arguments
    parser.add_argument("--file", "-f", type=str, help="File to be converted from 3D to 2D MIP")
    parser.add_argument("--read_path", "-p", help="Path to the file. Default = current folder.", default=".")
    parser.add_argument("--suffix", "-s", help="Suffix to be added to the filename. Default = _MIP", default = "_MIP")
    parser.add_argument("--channel_number", "-c", type=int, help="Number of channels in the image.")
    parser.add_argument("--output_folder", "-o", help="Path to the output file. Creates the folder if doesn't exist. Default = current folder.", default=".")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the argument values
    file = args.file
    read_path = args.read_path
    suffix = args.suffix
    channelnumber = args.channel_number
    output_folder = args.output_folder
    
    # Create the MIP stack and save
    img_array = read_tif(file, read_path)
    mip_img_array = mip_tif(img_array, channelnumber)
    save_tif(mip_img_array, file, output_folder, suffix)
