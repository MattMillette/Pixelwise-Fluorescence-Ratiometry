# -*- coding: utf-8 -*-

from glob import glob
from PIL import Image
import os
import csv

###########################################################################
## User-set thresholds

## manually determine and set background threshold
background_max = 1500
## set maximum ranges here
max_red_intensity = 50000
max_green_intensity = 65000
## minimum accepted pixels per image
minimum_pixels = 100

###########################################################################

## undetected pixels
undetected = 0

## create empty list outside loop for ratios, set naming schemes
## red and green IDs refer to chunks so ignore original images are ignored
red_id = "red"
green_id = "green"
file_extension = ".tif"
output_file = "_ratios" + ", background_max " + str(background_max) + ", max_G_intensity " + str(max_green_intensity) + ", max_R_intensity " + str(max_red_intensity) + ", minimum_pixels " + str(minimum_pixels) + ", undetected_green " + str(undetected) + ".csv"

import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()

directory = filedialog.askdirectory()
subdirectory = [os.path.abspath(x[0]) for x in os.walk(directory)]
subdirectory.remove(os.path.abspath(directory))

def analyze(subdirectory):
    ratios = [ ]
    file_list = glob(subdirectory + "/" + "*" + red_id + "*" + file_extension)

    for img in file_list:
        red_image = img
        green_image = img.replace(red_id, green_id)

        red = []
        green = []
        
        img = Image.open(red_image)
        w,h = img.size
        for y in range(h):
          for x in range(w):
            red.append((img.getpixel((x,y))))
    
        img = Image.open(green_image)
        w,h = img.size
        for y in range(h):
          for x in range(w):
            green.append((img.getpixel((x,y))))

        red_background = [i for i,x in enumerate(red) if x <= background_max]
        for background in reversed(red_background):
            del green[background]
            del red[background]
    
        green_saturated = [i for i,x in enumerate(green) if x == max_green_intensity]
        for saturated in reversed(green_saturated):
            del red[saturated]
            del green[saturated]
    
        red_saturated = [i for i,x in enumerate(red) if x == max_red_intensity]
        for saturated in reversed(red_saturated):
            del green[saturated]
            del red[saturated]
            
        green_undetected = [i for i,x in enumerate(green) if x == undetected]
        for empty in reversed(green_undetected):
            del red[empty]
            del green[empty]

        res = [g/r for g,r in zip(green, red)]

        res_sum = sum(res)

        total_pixels = len(red)
        if total_pixels < minimum_pixels:
                ratio = "empty"        
        elif total_pixels >= minimum_pixels:

            ratio = float(res_sum)/float(total_pixels)
            print (ratio)

        ratios.append(ratio)
        experimental_condition = os.path.basename(subdirectory)
        ratios_with_header = [experimental_condition]+ratios
    
    with open(directory + output_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(ratios_with_header)
    f.close()        
    
from timeit import default_timer as timer
start = timer()

for i in subdirectory:
    os.chdir(i)         
    analyze(i)
    
end = timer()
print ("Completed in: "+ str(end - start) +" seconds.")