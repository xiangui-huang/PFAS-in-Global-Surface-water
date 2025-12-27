# -*- coding: utf-8 -*-
"""
This program is dedicated to plot and extract nighttime light intensity data from the VNL database released by Colorado School of Mines.
re-sampling from VIIRS NTL (VNL) (cell size 0.4607, 0.4638) km with large cell size of (5.071, 5.102) km.
Created on Sun Dec  8 08:36:27 2024

@author: xiang
"""
import numpy as np
import pandas as pd

import geopandas as gpd
import geopy.distance

import rasterio
from rasterio.plot import show

#Define a function - Generating the resampling matrix with size of (5.071, 5.102) km.
def Resampling_array_fun(sampling_point, extension_number, xmin, xmax, ymin, ymax):
    deltaY_degree= 0.004166666
    deltaX_degree=0.0041666667
    
    upper_left_point=(sampling_point[0]-extension_number*deltaX_degree, sampling_point[1]+extension_number*deltaY_degree)
    #upper_right_point=(sampling_point[0]+extension_number*deltaX_degree, sampling_point[1]+extension_number*deltaY_degree)
    #bottom_left_point=(sampling_point[0]-extension_number*deltaX_degree, sampling_point[1]-extension_number*deltaY_degree)
    #bottom_right_point=(sampling_point[0]+extension_number*deltaX_degree, sampling_point[1]-extension_number*deltaY_degree)
    
    #generating the 11*11 2D array
    ncol, nrow = (11, 11)
    Resampling_point_list=list([])
    
    for row_index in range(0, nrow):
      for col_index in range(0, ncol):
          xi= upper_left_point[0] + col_index*deltaX_degree
          yi= upper_left_point[1] - row_index*deltaY_degree
          Resampling_point_list=Resampling_point_list+[(xi, yi)]
                        
    #remove the snippets that out of raster file boundary.
    #check the y value
    Outlier_index=[]
    for i in range(0, nrow*ncol):
        xi=Resampling_point_list[i][0]
        yi=Resampling_point_list[i][1]
        
        if yi > ymax or yi < ymin:
            Outlier_index=Outlier_index.append(i)
        if xi > xmax or xi < xmin:
            Outlier_index=Outlier_index.append(i)
            
    if len(Outlier_index) > 0:
        for i in Outlier_index:
            del Resampling_point_list[i]
    
    return(Resampling_point_list)
# The end of this function. 





#The main part of program.       

"""
for col_i in range (0, 11):
    print(Resampling_list[55+col_i])
    
for col_i in range (0, 11):
    print(Resampling_list[11*col_i+0])
    
"""  
#reading the coordinate reference system data from csv file.
rcs_file="C:\Aphd_PFASs in Natural water\PFASs in surface water\Basic sample data and analysis\Sampling point distribution\Sampling Point.csv"
df = pd.read_csv(rcs_file,header=0)
df = df.dropna()
#sum_point=len(df)
#print (sum_point)

#The sample coordinate with CRS of EPSG:4326.
sample_ID=df['Name']
x_df = df['Longitude']
y_df = df['Latitude']
coords=[(x,y) for x,y in zip(x_df, y_df)]
#print(coords[0], ", ", coords[25])




# Open the rsaster data file from the same folder.
VNL_tif='VNL_npp_2023_average_masked.tif'
with rasterio.open(VNL_tif) as src:
    #print("The basic properties of the tif file:")
    #print(src.crs)
    #print(src.bounds)
    
    
    #Resampling the VNL data for each water sample point.
    extension_number=5
    xmin,xmax=(-180.00208333335, 180.00208621335)
    ymin, ymax=(-65.00208445335001, 75.00208333335)
    Resampled_VNL_list=[]
    
    for sampling_point in coords:
       Resampling_point_list= Resampling_array_fun(sampling_point, extension_number, xmin, xmax, ymin, ymax)
       VNL_list=[Z for Z in src.sample(Resampling_point_list)]
       VNL_list=[Z[0] for Z in VNL_list]
       Resampled_VNL=sum(VNL_list)/len(VNL_list)
       Resampled_VNL_list=Resampled_VNL_list+[Resampled_VNL]
       
    
#print("VNL (unit:nW cm-2 sr-1) at [0-9] is ", VNL_value[0:9])



#creat dataframe.
VNL_value_df=pd.DataFrame()
VNL_value_df["VNL"]=Resampled_VNL_list
VNL_value_df["Sample_ID"]=sample_ID

#write the VNL data to a csv file.
VNL_value_df.to_csv("Resampled_VNL_data.csv", index=False)
print(VNL_value_df.head())








print('The end of this program.')


