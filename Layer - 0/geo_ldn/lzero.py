import argparse
import ee
import math
import geemap
from ee_plugin import Map
import calendar
import os

c = calendar.Calendar()
import sys

if not hasattr(sys, 'argv'):
    sys.argv = ['']


# ========================== Arguments =========================

parser = argparse.ArgumentParser()

parser.add_argument('-te', type=str, nargs=4, help='specify the coordinate bounds for clipping')
parser.add_argument('-tek', type=str, help='specify the klm shape file path')
parser.add_argument('-tes', type=str, help='specify the shape file path')

parser.add_argument('-tr', type=str, nargs=2, help='Specify the spatial resolution')
parser.add_argument('-tt', type=str, nargs=2, help='Specify the temporal resolution')

parser.add_argument('-m', help='This flag will return monthly mean', action='store_true')
parser.add_argument('-y', help='This flag will return yearly mean', action='store_true')
parser.add_argument('-d', help='This flag will return a single image mean of all the time range', action='store_true')

parser.add_argument('-PC', help='This flag will provide Protrusion Coefficient files in the output', action='store_true')
parser.add_argument('-Zo', help='This flag will provide Zo (aerodynamic local roughnesslength extraction files in the output', action='store_true')

parser.add_argument('-a', type=float, help='value of a in (PC = a*ln(Zo) + b)')
parser.add_argument('-b', type=float, help='value of b in (PC = a*ln(Zo) + b)')

parser.add_argument('-pre_ft', type=str, help='This will add prefix to the output files')

args = parser.parse_args()
#args.te = ['70.0', '24.0', '74.0', '28.0']

# ========================= Global Varibales ====================
evi = None
clipper = None
spatial_extent = None
output_scale = None
x_spatial_res = None
y_spatial_res = None
epsg_code = None
start_date = None
end_date = None
schedule = None
prefix = None
utm_zone = None
a = 0.05
b = 0.26
some_alt = None
# arguments check

# ==================================================================

def clip_mask(unclipped_image):
    if args.te:
        clipped_image = unclipped_image.clip(spatial_extent)
        return clipped_image
    elif args.tek:
        # mask_image = geemap.shp_to_ee(args.tek)
        # clipped_image = unclipped_image.clip(mask_image)
        # return clipped_image
        pass
    elif args.tes:
        mask_image = geemap.shp_to_ee(args.tes)
        clipped_image = unclipped_image.clip(mask_image)
        return clipped_image

def convertDate(start_date, end_date):
    start_year = int(start_date.split('/')[0])
    end_year = int(end_date.split('/')[0])
    start_m = int(start_date.split('/')[1])
    start_day = int(start_date.split('/')[2])
    end_m = int(end_date.split('/')[1])
    end_day = int(end_date.split('/')[2])
    startDate = ee.Date.fromYMD(start_year, start_m, start_day)
    endDate = ee.Date.fromYMD(end_year, end_m, end_day)
    return startDate, endDate

def help_calculate(filter_data, date, vizParams, output_name, expression):
    data = filter_data
    if expression != None:
        layer = eval(expression)
    else:
        layer = data
    if clipper != None:
        layer = clip_mask(layer)
    try:
        Map.centerObject(layer, 8)
    except:
        pass
    #Map.addLayer(layer, vizParams, '{}_{}_{}'.format(prefix, date, output_name))
    export(layer, "{}_{}_{}".format(prefix, date, output_name))

def calculate(data, schedule, start_date, end_date, vizParams, output_name, expression):
    start_year = int(start_date.split('/')[0])
    end_year = int(end_date.split('/')[0])
    
    if schedule == 'yearly':

        for i in range(start_year, end_year + 1):

            if (i == start_year):
                start_m = int(start_date.split('/')[1])
                start_day = int(start_date.split('/')[2])
            else:
                start_m = 1
                start_day = 1

            if (i == end_year):
                end_m = int(end_date.split('/')[1])
                end_day = int(end_date.split('/')[2])
            else:
                end_m = 12
                end_day = 31

            startDate = ee.Date.fromYMD(i, start_m, start_day)
            endDate = ee.Date.fromYMD(i, end_m, end_day)
            filter_data = data.filterDate(startDate, endDate)
            date = i
            help_calculate(filter_data, date, vizParams, output_name, expression)

    elif schedule == 'monthly':

        start_m = int(start_date.split('/')[1])

        for i in range(start_year, end_year + 1):

            if i != start_year:
                start_m = 1
                start_day = 1

            if i != end_year:
                end_m = 12

            else:
                end_m = int(end_date.split('/')[1])

            month = end_m
            current_m = start_m

            while (month > 0 and current_m <= end_m):

                if ((i == start_year) and (current_m == int(start_date.split('/')[1]))):
                    start_day = int(start_date.split('/')[2])
                else:
                    start_day = 1

                if ((i == end_year) and (current_m == int(end_date.split('/')[1]))):
                    end_day = int(end_date.split('/')[2])
                else:
                    end_day = calendar.monthrange(i, current_m)[-1]

                startDate = ee.Date.fromYMD(i, current_m, start_day)
                endDate = ee.Date.fromYMD(i, current_m, end_day)
                filter_data = data.filterDate(startDate, endDate)
                date = str(i) + '/' + str(current_m)
                help_calculate(filter_data, date, vizParams, output_name, expression)
                month -= 1
                current_m += 1

    else:
        vizParams = {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}
        start = start_date.replace('/', '-')
        end = end_date.replace('/', '-')
        data = data.filterDate(start, end)
        help_calculate(data, start, vizParams, output_name, expression)

output_directory = os.path.join(os.path.expanduser('~'), 'Desktop')
def export(layer, name):
    out_dir = output_directory
    name = name.replace('/', '_')
    name = name + '.tif'
    filename = os.path.join(out_dir, name)
    if clipper == None:
        geemap.ee_export_image(layer, filename = filename, crs = epsg_code, scale = output_scale)
    else:
        geemap.ee_export_image(layer, filename = filename, region = clipper, crs = epsg_code, scale = output_scale)

def wind_speed(image):
    wind_speed = image.expression("((u**2) + (v**2))**(1/2)",{
        'u' : image.select('u_component_of_wind_10m'),
        'v' : image.select('v_component_of_wind_10m')
    }).rename('wind_speed')

    return image.addBands(wind_speed)

def wind_dir(image):
    wind_u = image.select('u_component_of_wind_10m')
    wind_v = image.select('v_component_of_wind_10m')
    wind_dir = wind_v.divide(wind_u).atan().rename('wind_dir')
    degree = 180/math.pi
    wind_dir = wind_dir.multiply(degree)

    return image.addBands(wind_dir)

def landSurfaceTemp(LST):

    vizParams = {'min': -13.15, 'max': 56.85, 'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
    '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef', '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
    'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d', 'ff0000', 'de0101', 'c21301', 'a71001', '911003']}
    output_name = 'lst'
    expression = "(data.mean().multiply(0.02).subtract(273.15).rename('Land Surface Temperature'))"
    calculate(LST, schedule, start_date, end_date, vizParams, output_name, expression)
    

def modisEVI(EVI):
    vizParams = {'min': 0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
    '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']}
    output_name = 'modis_evi'
    expression = "(data.mean().multiply(0.0001).rename('Enhanced Vegetation Index_MODIS'))"
    calculate(EVI, schedule, start_date, end_date, vizParams, output_name, expression)


def landsat5EVI(EVI):
    vizParams = {'min': -1.0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
    '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']}
    output_name = 'l5_evi'
    expression = "(data.mean().rename('Enhanced Vegetation Index_L5'))"
    calculate(EVI, schedule, start_date, end_date, vizParams, output_name, expression)


def landsat8EVI(EVI):
    vizParams = {'min': -1.0, 'max': 1.0, 'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
    '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']}
    output_name = 'l8_evi'
    expression = "(data.mean().rename('Enhanced Vegetation Index_L8'))"
    calculate(EVI, schedule, start_date, end_date, vizParams, output_name, expression)


def clayFraction(clay, sand, silt):
    denominator = clay.add(sand).add(silt)
    clay_fraction = clay.multiply(100).divide(denominator).rename("Clayfraction_0-5cm_mean")
    vizParams = {'min':0, 'max':100, 'palette': ['red', 'green', 'blue', 'cyan', 'orange', 'yellow']}
    output_name = 'clay_fraction'
    exportWithoutDate(clay_fraction, vizParams, output_name)


def bulkDensity(bdod):
    vizParams = {'min':0, 'max':174, 'palette': ['red', 'green', 'blue', 'cyan', 'orange', 'yellow']}
    output_name = 'bulk_density'
    exportWithoutDate(bdod, vizParams, output_name)

def soilCarbon(soc):
    vizParams = {'min':0, 'max':212, 'palette': ['yellow', 'green', 'cyan', 'blue']}
    output_name = 'soc_stock'
    exportWithoutDate(soc, vizParams, output_name)
    

def landCoverData(landcover):
    vizParams = {'min': 11, 'max': 210, 'palette': ['05450a', '086a10', '54a708', '78d203', '009900', 'c6b044', 'dcd159',
    'dade48', 'fbff13', 'b6ff05', '27ff87', 'c24f44', 'a5a5a5', 'ff6d4c', '69fff8', 'f9ffa4', '1c0dff']}
    start_year = int(start_date.split('/')[0])
    end_year = int(end_date.split('/')[0])
    output_name = 'landcover'
    expression = "data.rename('{}_{}_{}'.format(prefix, date, output_name))"
    for i in range(start_year, end_year+1):
        date = i
        # reclassify lc to ipcc classes
        # Handle case of year_start that isn't included in the CCI data
        if date > 2018:
            date = 2018
        elif date < 1992:
            date = 1992
        else:
            lc_year_start = start_year
        filter_data = landcover.select('y{}'.format(date))\
                .remap([10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82, 90, 100, 160, 170, 110, 130, 180, 190, 120, 121, 122, 140, 150, 151, 152, 153, 200, 201, 202, 210], 
               [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36])
        help_calculate(filter_data, date, vizParams, output_name, expression)


def netPrimaryProductivity(npp):
    vizParams = {'min': 0.0, 'max': 19000.0, 'palette': ['bbe029', '0a9501', '074b03']};
    start_year = int(start_date.split('/')[0])
    end_year = int(end_date.split('/')[0])
    output_name = 'npp'
    expression = "data.mean().multiply(0.0001).rename('{}_{}_{}'.format(prefix, date, output_name))"
    for i in range(start_year, end_year+1):
        date = i
        filter_data = npp.filterMetadata("system:index", 'contains', '{}'.format(date));
        help_calculate(filter_data, date, vizParams, output_name, expression)
        

def addPC(image):
    PC = image.expression("(b2)/(b1)", {
        'b2': image.select("BRDF_Albedo_Parameters_Band1_vol"),
        'b1': image.select("BRDF_Albedo_Parameters_Band1_iso"),
    }).rename('PC')
    return image.addBands(PC)


def addZo(image):
    divider = math.exp(b/a)
    Zo = image.divide(a).exp().divide(divider).rename('Zo')
    #tmp = image.subtract(b)
    #tmp1 = tmp.divide(a)
    #Zo = tmp1.exp().rename('Zo')
    return image.addBands(Zo)
    

def PC_Zo(BRDF):
    vizParams = {'min':0, 'max':3, 'palette': ['red', 'yellow','green']}
    PC = BRDF.map(addPC).select('PC')
    output_name = 'pc'
    expression = "data.mean().rename('{}_{}_{}'.format(prefix, date, output_name))"
    calculate(PC, schedule, start_date, end_date, vizParams, output_name, expression)
    Zo = PC.map(addZo).select('Zo')
    output_name = 'zo'
    expression = "data.mean().rename('{}_{}_{}'.format(prefix, date, output_name))"
    calculate(Zo, schedule, start_date, end_date, vizParams, output_name, expression)

#=============================BRDF==================================

def brdfCalculate(BRDF):

    # with open('/home/naruto/BRDF.text', 'w') as file:
    #     file.write('a' + schedule + 'b')
    
    vizParams = {'min':0, 'max':1, 'gamma':2}
    BRDF_band1 = BRDF.select('BRDF_Albedo_Parameters_Band1_iso','BRDF_Albedo_Parameters_Band1_vol','BRDF_Albedo_Parameters_Band1_geo')
    BRDF_band2 = BRDF.select('BRDF_Albedo_Parameters_Band2_iso','BRDF_Albedo_Parameters_Band2_vol','BRDF_Albedo_Parameters_Band2_geo')
    BRDF_band3 = BRDF.select('BRDF_Albedo_Parameters_Band3_iso','BRDF_Albedo_Parameters_Band3_vol','BRDF_Albedo_Parameters_Band3_geo')
    output_name = 'brdf_band1'
    expression = "data.mean().multiply(0.001).rename('{}_{}_{}_iso'.format(prefix, date, output_name),'{}_{}_{}_vol'.format(prefix, date, output_name),'{}_{}_{}_geo'.format(prefix, date, output_name))"
    calculate(BRDF_band1, schedule, start_date, end_date, vizParams, output_name, expression)
    output_name = 'brdf_band2'
    expression = "data.mean().multiply(0.001).rename('{}_{}_{}_iso'.format(prefix, date, output_name),'{}_{}_{}_vol'.format(prefix, date, output_name),'{}_{}_{}_geo'.format(prefix, date, output_name))"
    calculate(BRDF_band2, schedule, start_date, end_date, vizParams, output_name, expression)
    output_name = 'brdf_band3'

    expression = "data.mean().multiply(0.001).rename('{}_{}_{}_iso'.format(prefix, date, output_name),'{}_{}_{}_vol'.format(prefix, date, output_name),'{}_{}_{}_geo'.format(prefix, date, output_name))"
    calculate(BRDF_band3, schedule, start_date, end_date, vizParams, output_name, expression)


def exportWithoutDate(layer, vizParams, output_name):
    if clipper != None:
        layer = clip_mask(layer)
    try:
        Map.centerObject(layer, 8)
    except:
        pass
    #Map.addLayer(layer, vizParams, '{}_{}'.format(prefix, output_name))
    export(layer, "{}_{}".format(prefix, output_name))


def ecmwf(ECMWF):
    vizParams = {'palette': ["#000080","#0000D9","#4000FF","#8000FF","#0080FF","#00FFFF","#00FF80","#80FF00","#DAFF00","#FFFF00","#FFF500","#FFDA00","#FFB000","#FFA400","#FF4F00","#FF2500","#FF0A00","#FF00FF"]}

    ERA5_soil_band = ECMWF.select('volumetric_soil_water_layer_1')
    output_name = 'soil_moisture'
    expression = "data.mean().rename('{}_{}_{}'.format(prefix, date, output_name))"
    calculate(ERA5_soil_band, schedule, start_date, end_date, vizParams, output_name, expression)

    ECMWF_wind_direction = ECMWF.map(wind_dir).select('wind_dir')
    output_name = 'wind_direction'
    expression = "data.mean().rename('{}_{}_{}'.format(prefix, date, output_name))"
    calculate(ECMWF_wind_direction, schedule, start_date, end_date, vizParams, output_name, expression)

    ECMWF_wind_speed = ECMWF.map(wind_speed).select('wind_speed')
    output_name = 'wind_speed'
    expression = "data.mean().rename('{}_{}_{}'.format(prefix, date, output_name))"
    calculate(ECMWF_wind_speed, schedule, start_date, end_date, vizParams, output_name, expression) 

    ERA5_snow_cover_band = ECMWF.select('snow_cover')
    output_name = 'snow_cover'
    expression = "data.mean().rename('{}_{}_{}'.format(prefix, date, output_name))"
    calculate(ERA5_snow_cover_band, schedule, start_date, end_date, vizParams, output_name, expression)


def qa_filter(img):
        mask = img.select('SummaryQA')
        mask = mask.where(img.select('SummaryQA').eq(-1), 0)
        mask = mask.where(img.select('SummaryQA').eq(0), 1)
        mask = mask.where(img.select('SummaryQA').eq(1), 1)
        mask = mask.where(img.select('SummaryQA').eq(2), 0)
        mask = mask.where(img.select('SummaryQA').eq(3), 0)
        masked = img.select('EVI').updateMask(mask)
        return masked

def main_run():
    # ====================================== LST ================================================
    LST = ee.ImageCollection("MODIS/006/MOD11A1")
    LST = LST.select('LST_Day_1km')
    landSurfaceTemp(LST)

    #======================================= EVI ===================================================
    if (evi == 'modis'):
        EVI = ee.ImageCollection("MODIS/006/MOD13Q1")
        # EVI = EVI.map(qa_filter)
        EVI = EVI.select('EVI')
        modisEVI(EVI)
    elif evi == 'landsat5':
        EVI = ee.ImageCollection("LANDSAT/LT05/C01/T1_8DAY_EVI")
        EVI = EVI.select('EVI')
        landsat5EVI(EVI)
    elif evi == 'landsat8':
        EVI = ee.ImageCollection("LANDSAT/LC08/C01/T1_8DAY_EVI")
        EVI = EVI.select('EVI')
        landsat8EVI(EVI)

    #========================================= CLAY ================================================
    clay = ee.Image("projects/soilgrids-isric/clay_mean")
    clay = clay.select("clay_0-5cm_mean")
    sand = ee.Image("projects/soilgrids-isric/sand_mean")
    sand = sand.select("sand_0-5cm_mean")
    silt = ee.Image("projects/soilgrids-isric/silt_mean")
    silt = silt.select("silt_0-5cm_mean")
    clayFraction(clay, sand, silt)
        
    # # #========================================== BDOD =============================================
    bdod = ee.Image("projects/soilgrids-isric/bdod_mean")
    bdod = bdod.select("bdod_0-5cm_mean")
    bulkDensity(bdod)

    # #========================================== ECMWF ==============================================
    ECMWF = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY")
    ecmwf(ECMWF)
    
    # #====================================== Soil Organic Carbon Stock ==============================
    soc = ee.Image("projects/soilgrids-isric/ocs_mean")
    soc = soc.select("ocs_0-30cm_mean")
    soilCarbon(soc)

    # #========================================== Landcover ==========================================
    landcover = ee.Image("users/geflanddegradation/toolbox_datasets/lcov_esacc_1992_2018")
    landcover = landcover.where(landcover.eq(9999), -32768)
    landcover = landcover.updateMask(landcover.neq(-32768))
    landCoverData(landcover)
    
    # #========================================== Net Primary Productivity ===========================
    npp = ee.ImageCollection('MODIS/006/MOD17A3HGF').select('Npp')
    netPrimaryProductivity(npp)
    
    
    # #========================================== BRDF ===============================================
    startDate,endDate = convertDate(start_date, end_date)
    BRDF = ee.ImageCollection("MODIS/006/MCD43A1").filterDate(startDate, endDate).filterBounds(spatial_extent)
    PC_Zo(BRDF)
    brdfCalculate(BRDF)