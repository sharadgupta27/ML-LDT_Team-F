from PIL import Image, ImageFilter
import gdal
import numpy as np
import tensorflow as tf
from osgeo import osr
import cv2
from sklearn.preprocessing import MinMaxScaler

def generate_input(pc_dir, lst_dir, evi_dir, out_dir):

  img_pc = gdal.Open(pc_dir)
  img_lst = gdal.Open(lst_dir)
  img_evi = gdal.Open(evi_dir)

  a_array = img_pc.GetRasterBand(1).ReadAsArray()
  b_array = img_lst.GetRasterBand(1).ReadAsArray()
  c_array = img_evi.GetRasterBand(1).ReadAsArray()

  globals()['width'] = img_pc.RasterXSize
  globals()['height'] = img_pc.RasterYSize
  globals()['geotransform_info'] = img_pc.GetGeoTransform()
  globals()['projection_info'] = img_pc.GetProjection()

  img_pc_1 = np.array(a_array)
  img_lst_1 = np.array(b_array)
  img_evi_1 = np.array(c_array)

  img = np.stack((img_pc_1,img_lst_1,img_evi_1))
  norm_image = cv2.normalize(img, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_32F)
  norm_image = np.uint8(norm_image)

  out_name = out_dir + '\\input_image.png'

  new_img = np.zeros((norm_image.shape[1], norm_image.shape[2], 3))
  new_img[:, :, 0] = norm_image[0, :, :]
  new_img[:, :, 1] = norm_image[1, :, :]
  new_img[:, :, 2] = norm_image[2, :, :]


  cv2.imwrite(out_name, new_img)
  return out_name


#=================================================
#=================================================
#=================================================
#=================================================


def weighted_binary_crossentropy(y_true, y_pred):
  class_loglosses = K.mean(K.binary_crossentropy(y_true, y_pred), axis=[0, 1, 2])
  return K.sum(class_loglosses * K.constant(class_weights))


def predict_image(original_image_path, model_path, out_dir):

  img = gdal.Open(original_image_path)

  imarray = img.ReadAsArray()

  bands, rows, cols = imarray.shape

  upperlimit_X = int(np.ceil(rows/256))
  upperlimit_Y = int(np.ceil(cols/255))

  img_new = np.zeros((upperlimit_X*256, upperlimit_Y*256, bands))
  pred_img = np.zeros((upperlimit_X*256, upperlimit_Y*256))
  img_new[:rows, :cols, 0] = imarray[0, :, :]
  img_new[:rows, :cols, 1] = imarray[1, :, :]
  img_new[:rows, :cols, 2] = imarray[2, :, :]


  model = tf.keras.models.load_model(model_path, custom_objects={'weighted_binary_crossentropy':                   
                                      weighted_binary_crossentropy})

  for i in range(upperlimit_Y):
    for j in range(upperlimit_X):

      y_start_idx = i*256
      y_end_idx = y_start_idx + 256

      x_start_idx = j*256
      x_end_idx = x_start_idx + 256

      img_to_pred = img_new[x_start_idx:x_end_idx, y_start_idx:y_end_idx, :]
      img_to_pred = img_to_pred.reshape((1,256,256,3))

      result = model.predict(img_to_pred)[:,:,:,0]
      result = result.reshape((256,256))

      pred_img[x_start_idx:x_end_idx, y_start_idx:y_end_idx] = result

  final = pred_img[:rows, :cols]

  final = Image.fromarray(final)
  final = final.filter(ImageFilter.MedianFilter(size = 5)) 
  final = np.array(final)
    
  out_name = out_dir + '/predicted_erosion.tif'

  driver = gdal.GetDriverByName("GTiff")
  output_file = out_name
  output_tiff = driver.Create(output_file,width,height,1,gdal.GDT_Float64)
  output_tiff.GetRasterBand(1).WriteArray(final)
  output_tiff.GetRasterBand(1).SetNoDataValue(-9999)
  output_tiff.SetGeoTransform(geotransform_info)
  srs = osr.SpatialReference()
  srs.ImportFromWkt(projection_info)
  output_tiff.SetProjection( srs.ExportToWkt() )
  output_tiff = None
  
  return out_name
