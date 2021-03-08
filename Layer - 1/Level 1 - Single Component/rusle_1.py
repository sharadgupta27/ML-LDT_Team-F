import gdal
import numpy as np
from osgeo import gdal,osr
import os
from functools import reduce
from sklearn.preprocessing import MinMaxScaler
output_directory = None

def first(norm):
    R=gdal.Open(output_directory + '\RUSLE_RFactor.tif')
    C=gdal.Open(output_directory + '\RUSLE_CFactor.tif')
    K=gdal.Open(output_directory + '\RUSLE_KFactor.tif')
    LS=gdal.Open(output_directory + '\RUSLE_LSFactor.tif')

    globals()['width']=R.RasterXSize
    globals()['height']=R.RasterYSize
    globals()['geotransform_info']=R.GetGeoTransform()
    globals()['projection_info'] =R.GetProjection()

    #converting  into numpy arrays
    R_array=R.GetRasterBand(1).ReadAsArray()
    C_array=C.GetRasterBand(1).ReadAsArray()
    K_array=K.GetRasterBand(1).ReadAsArray()
    LS_array=LS.GetRasterBand(1).ReadAsArray()
    
    a=np.empty([height,width],dtype=float)
    flux_list=list()
    for x in range(width):
        for y in range(height):
            aslpa=(float(R_array[y][x]))*(float(C_array[y][x]))*(float(K_array[y][x]))*(float(LS_array[y][x]))
            if aslpa>325:
                aslpa=325
            a[y][x]=aslpa

    if norm:
        a = MinMaxScaler().fit_transform(a)

    return a

shape_file = None
clipper = None
#export
def export_temp(a):
    driver = gdal.GetDriverByName("GTiff")
    output_file = output_directory + '/temp.tif'
    output_tiff = driver.Create(output_file,width,height,1,gdal.GDT_Float64)
    output_tiff.GetRasterBand(1).WriteArray(a)
    output_tiff.GetRasterBand(1).SetNoDataValue(-999)
    output_tiff.SetGeoTransform(geotransform_info)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection_info)
    output_tiff.SetProjection( srs.ExportToWkt() )
    output_tiff = None

def export_final():
    if clipper[-1] == 'shape':
        world_rusle = output_directory + '/temp.tif'
        clipped_rusle = output_directory + '/RUSLE.tif'
        result = gdal.Warp(clipped_rusle, world_rusle, cutlineDSName = shape_file)
    else:
        pass

