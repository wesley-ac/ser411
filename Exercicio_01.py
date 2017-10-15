# encoding: utf-8
"""
Exercício 01 - 05/10/17

Wesley Augusto Campanharo - 139203

 O objetivo é criar uma grade numérica com os valores mensais acumulados de
 números de focos de queimadas no ano de 2016 para cada sensor
 
"""

import sys #pacote do sistema para trabalhar com pastas e caminhos
import os # pacote do sistema operacional para mexer com nomes
import numpy as np

try:
    from osgeo import gdal,osr,ogr
except:
    sys.exit("Erro: a biblioteca GDAL não foi encontrada!")

from utils import *

#Definilção de constantes globais, normalmente são os arquivos de entrada
##Shapefile de focos a ser contado
vector_file = "./focos/focos-2016.shp"
vector_file_base_name = os.path.basename(vector_file) # armazena apenas o nome do arquivo
layer_name = os.path.splitext(vector_file_base_name)[0] #armazena apenas o caminho do arquivo


## Tipo do arquivo de saída
file_format = "Gtiff"
driver = gdal.GetDriverByName(file_format)
spatial_extent = {"xmin":-89.975, "ymin":-59.975, "xmax":-29.975, "ymax":10.025}
spatial_resolution = {"x":0.05, "y":0.05}
grid_dimension = {'cols':1200, 'rows':1400}


# Abrindo arquivo de focos
shp_focos = ogr.Open(vector_file)
if shp_focos is None:
    sys.exit("Erro: não foi possível abrir o arquivos '{0}'".format(vector_file))

layer_focos = shp_focos.GetLayer(layer_name)
if layer_focos is None:
    sys.exit("Erro: não foi possível acessar a camada '{0}' no arquivo '{1}'!".format(layer_name, vector_file))

#Descobrir o schema da shapefile
schema = []
tipo = []
ldefn = layer_focos.GetLayerDefn()
for n in range(ldefn.GetFieldCount()):
    fdefn = ldefn.GetFieldDefn(n)
    schema.append(fdefn.name)
    tipo.append(fdefn.GetTypeName())
print schema
print tipo

sensor = ('TERRA_M-M', 'TERRA_M-T', 'AQUA_M-T', 'AQUA_M-M')
meses = ('01','02','03','04','05','06','07','08','09','10','11','12')

#Filtro de Atributos
for s in sensor: #Filtro por tipo de Sensor 
    for d in meses: #Filtrar por meses
        layer_focos_fil = layer_focos
        layer_focos_fil.SetAttributeFilter("satelite = '{0}'".format(s))
        matriz = np.zeros((grid_dimension['rows'],grid_dimension['cols']),np.int16)
        for foco in layer_focos_fil:
            data = foco.GetFieldAsString(7)[5:7]
            if data == d:
                location = foco.GetGeometryRef()
                col, row = Geo2Grid(location, grid_dimension, spatial_resolution, spatial_extent)
                matriz[row, col] += 1
            else:
                continue
            
        output_file_name = "./output/{0}_{1}.tif".format(s,d)
        raster = driver.Create(output_file_name,grid_dimension['cols'],grid_dimension['rows'],1,gdal.GDT_Int16)
        if raster is None:
            sys.exit("Erro: não foi possível criar o arquivo '{0}'.".format(output_file_name))
       
        raster.SetGeoTransform((spatial_extent['xmin'],spatial_resolution['x'],0,spatial_extent['ymax'],0,-spatial_resolution['y']))
        srs_focos = layer_focos.GetSpatialRef()
        raster.SetProjection(srs_focos.ExportToWkt())
        band = raster.GetRasterBand(1)
        band.WriteArray(matriz,0,0)
        band.FlushCache()
        raster = None
        print("Arquivo {0} salvo - total de {1} focos".format(output_file_name,matriz.sum()))
del raster, band




# Links utilizados
"""
https://gis.stackexchange.com/questions/68650/ogr-how-to-save-layer-from-attributefilter-to-a-shape-filter
https://gis.stackexchange.com/questions/195323/selecting-by-attributes-and-making-new-shapefile-using-python-ogr-only
http://www.gdal.org/ogr_sql.html
https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
"""