from PIL.Image import NONE
from scipy.interpolate import CubicSpline
from scipy.interpolate import lagrange
import numpy as np
from osgeo import gdal,osr
import ogr
import osr
import os
import math
import scipy
import scipy.signal
from sklearn.preprocessing import MinMaxScaler

def interpolate(interpolate_year, interpolation_method, series_directory, output_directory, norm, LU):

    data = gdal.Open(str(series_directory))

    width = data.RasterXSize
    height = data.RasterYSize
    geotransform_info = data.GetGeoTransform()
    projection_info = data.GetProjection()
    bands = int(data.RasterCount)
    
    data_array = data.ReadAsArray()
    if 'evi' in series_directory.lower() or 'lst' in series_directory.lower():
        data_array = np.nan_to_num(data_array)
        x = np.arange(bands)

        new_raster = np.empty([height, width])
        n = int(interpolate_year) - 2018  # calculation of further bands n=1 means 149th band for an image with 148 bands
        for i in range(width):
            for j in range(height):

                y = np.empty([bands])

                for b in range(bands):
                    y[b] = data_array[b][j][i]
                if interpolation_method == "CubicSpline":
                    f2 = CubicSpline(x,y)
                    xnew=f2(bands+n)
                    new_raster[j][i]=xnew
                elif interpolation_method == "polynomial":
                    f2 = scipy.interpolate.BarycentricInterpolator(x, y)
                    xnew=f2(bands+n)
                    new_raster[j][i]=xnew
                elif interpolation_method == "linear":
                    f2 = scipy.interpolate.interp1d(x,y,kind='linear',fill_value="extrapolate")
                    xnew=f2(bands+n)
                    new_raster[j][i]=xnew

        new_raster1 = scipy.signal.medfilt(new_raster,kernel_size=3)

    if norm:
        pass

    out_name = output_directory

    if 'evi' in series_directory.lower():
        # for x in range(new_raster1.shape[0]):
        #     for y in range(new_raster1.shape[1]):
        #         if new_raster1[x][y] < -1:
        #             new_raster1[x][y] = -1
        #         if new_raster1[x][y] >= 1:
        #             new_raster1[x][y] = 1
        out_name = output_directory + '/interpolated_evi.tif'

    elif 'lst' in series_directory.lower():
        # for x in range(new_raster1.shape[0]):
            # for y in range(new_raster1.shape[1]):
            #     if new_raster1[x][y] < -10:
            #         new_raster1[x][y] = -10
            #     if new_raster1[x][y] >= 50:
            #         new_raster1[x][y] = 50       
        out_name = output_directory + '/interpolated_lst.tif'

    elif 'pc' in series_directory.lower():
        out_name = output_directory + '/pc_file.tif'

    if LU:
        vec_ds = ogr.Open(LU)
        lyr = vec_ds.GetLayer()
        drv_tiff = gdal.GetDriverByName("GTiff")
        out_name_LU = out_name.split('.')[0] + '_LU.tif'
        chn_ras_ds = drv_tiff.Create(out_name_LU, width, height, 1, gdal.Float32)
        chn_ras_ds.SetGeoTransform(geotransform_info)
        if 'pc' in series_directory.lower():
            gdal.RasterizeLayer(chn_ras_ds,[1],lyr,options=["ATTRIBUTE=Value1"])
        elif 'lst' in series_directory.lower():
            gdal.RasterizeLayer(chn_ras_ds,[1],lyr,options=["ATTRIBUTE=Value2"])
        elif 'evi' in series_directory.lower():
            gdal.RasterizeLayer(chn_ras_ds,[1],lyr,options=["ATTRIBUTE=Value3"])
        chn_ras_ds.GetRasterBand(1).SetNoDataValue(0.0)        
        chn_ras_ds = None
        usc = Gdal.Open(out_name_LU)
        user_scenario = usc.ReadAsArray()
        original_tiff = new_raster1
        max1 = np.max(user_scenario)
        final_array = np.empty([height, width], dtype = float)
        for x in range(width):
            for y in range(height):
                if user_scenario[y][x]==0.0:
                    final_array[y][x]=float(orignal_tif[y][x])
                else:
                    final_array[y][x]=user_scenario[y][x]

        driver = gdal.GetDriverByName("GTiff")
        output_file = output_name
        output_tiff = driver.Create(output_file,width,height,1,gdal.GDT_Float64)
        output_tiff.GetRasterBand(1).WriteArray(final_array)
        output_tiff.GetRasterBand(1).SetNoDataValue(-9999)
        output_tiff.SetGeoTransform(geot)
        srs = osr.SpatialReference()
        srs.ImportFromWkt(projection_info)
        output_tiff.SetProjection( srs.ExportToWkt() )
        output_tiff = None

    driver = gdal.GetDriverByName("GTiff")
    output_file = out_name
    output_tiff = driver.Create(output_file,width,height,1,gdal.GDT_Float64)
    output_tiff.GetRasterBand(1).WriteArray(new_raster1)
    output_tiff.GetRasterBand(1).SetNoDataValue(-999)
    output_tiff.SetGeoTransform(geotransform_info)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection_info)
    output_tiff.SetProjection( srs.ExportToWkt() )
    output_tiff = None