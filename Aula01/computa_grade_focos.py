# encoding: utf-8
# Aula 01 - 05/10/17
# O objetivo é criar uma grade numérica com os valores acumulados de números de focos de queimadas no ano de 2016


# Importando pacotes

import sys #pacote do sistema para trabalhar com pastas e caminhos
import os # pacote do sistema operacional para mexer com nomes
import numpy as np

#mecanismo pra deixar o programa mais bonito quando não tiver a gdal instalada
try:
    from osgeo import gdal,osr,ogr
except:
    sys.exit("Erro: a biblioteca GDAL não foi encontrada!")

from utils import * #Da função Geo2Grid criada anteriormente será importado para este script agora


#Para se incluir a gdal dentro do "Try Exceptio" é necessário incluir as bibliotecas no UseExceptions
gdal.UseExceptions()
ogr.UseExceptions()
osr.UseExceptions()

#Definilção de constantes globais, normalmente são os arquivos de entrada
##Shapefile de focos a ser contado
vector_file = "/home/labgeo8/Dados/Queimadas/focos/focos-2016.shp"
vector_file_base_name = os.path.basename(vector_file) # armazena apenas o nome do arquivo
layer_name = os.path.splitext(vector_file_base_name)[0] #armazena apenas o caminho do arquivo

## Variáveis para criação da grade, lembrando que devem permanecer no tipo de construção "Dicionario"
# além de deixar os nomes das chaves como as que já estão
spatial_extent = {"xmin":-89.975, "ymin":-59.975, "xmax":-29.975, "ymax":10.025}
spatial_resolution = {"x":0.05, "y":0.05}
grid_dimension = {'cols':1200, 'rows':1400}


## Tipo do arquivo de saída
file_format = "Gtiff"
output_file_name = "/home/labgeo8/Dados/Queimadas/focos/grade_2016.tif"


# Abrindo aquivo vetorial
shp_focos = ogr.Open(vector_file)

if shp_focos is None:
    sys.exit("Erro: não foi possivel abrir o arquivo {0} !".format(vector_file))
else:
    print("Arquivo {0} aberto com sucesso !".format(vector_file))

# como a gdal abre o arquivo como um data........ é necessário pegar apenas a camada espacial, o layer
# O layer é um conjunto de feições (atributo+geometry)
layer_focos = shp_focos.GetLayer(layer_name)

if layer_focos is None:
    sys.exit("Erro: não foi possivel acessar a camada {1} do arquivo {0}!".format(vector_file,layer_focos))
else:
    print("Layer carregado com sucesso!")


# Criando uma matriz numerica para gerar a grade
matriz = np.zeros((grid_dimension['rows'],grid_dimension['cols']),np.uint16)


# Fazendo a interação com cada foco para determinar onde ele se encontra na grade, armazenando na matriz

for foco in layer_focos:
    location = foco.GetGeometryRef()
    col,row = Geo2Grid(location,grid_dimension,spatial_resolution,spatial_extent)

    matriz[row,col]+=1


# Criando o arquivo Tiff da matriz das contas
driver = gdal.GetDriverByName(file_format)

if driver is None:
    sys.exit("Erro: arquivo não encontrado")


raster = driver.Create(output_file_name,grid_dimension['cols'],grid_dimension['rows'],1,gdal.GDT_UInt16)

if raster is None:
    sys.exit("Erro: O arquivo {0} não pode ser criado".format(output_file_name))


# configurando o extent do GeoTiff
raster.SetGeoTransform((spatial_extent['xmin'],spatial_resolution['x'],0,spatial_extent['ymax'],0,-spatial_resolution['y']))

# Irá usar a mesma referencia do arquivo de focos
srs_focos = layer_focos.GetSpatialRef()
raster.SetProjection(srs_focos.ExportToWkt())

band = raster.GetRasterBand(1)
band.WriteArray(matriz,0,0)

# Essas duas fuções são para o jupyter liberar memoria do cache
band.FlushCache()
raster = None