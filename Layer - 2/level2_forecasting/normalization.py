import gdal
import ogr
import osr
import numpy as np
import os
import math
Unccd=gdal.Open('D:\\UNCCD_SDS_Output.tif')
Eof_lst=gdal.Open('D:\\EOF_of_LST_Final.tif')
globals()['width']=Unccd.RasterXSize
globals()['height']=Unccd.RasterYSize
globals()['geotransform_info']=Unccd.GetGeoTransform()
globals()['projection_info'] =Unccd.GetProjection()
globals()['bands']=int(Unccd.RasterCount)
Unccd_array=Unccd.ReadAsArray()
Eof_lst_array=Eof_lst.ReadAsArray()
Unccd_array1d=Unccd_array.reshape(width*height,1)
Eof_lst_array1d=Eof_lst_array.reshape(width*height,1)

ref_vec=np.ma.masked_invalid(Unccd_array1d)
img_vec=np.ma.masked_invalid(Eof_lst_array1d)


filtered_img=np.ma.masked_equal(img_vec,0.0)
filtered_ref=np.ma.masked_equal(ref_vec,0.0)

r_max=np.max(filtered_ref)
r_min=np.min(filtered_ref)

i_max=np.mean(filtered_img,axis=0)+3.5*np.std(filtered_img,axis=0)
i_min=np.mean(filtered_img,axis=0)-3.5*np.std(filtered_img,axis=0)
gain=(r_max-r_min)/(i_max-i_min)
final_array=np.empty([height,width],dtype=float)
new_img=gain*(Eof_lst_array-i_min)

driver = gdal.GetDriverByName("GTiff")
output_file ='D:\\Prarit Data\\normal.tif'
output_tiff = driver.Create(output_file,width,height,1,gdal.GDT_Float64)
output_tiff.GetRasterBand(1).WriteArray(new_img)
output_tiff.GetRasterBand(1).SetNoDataValue(-999)
output_tiff.SetGeoTransform(geotransform_info)
srs = osr.SpatialReference()
srs.ImportFromWkt(projection_info)
output_tiff.SetProjection( srs.ExportToWkt() )
output_tiff = None