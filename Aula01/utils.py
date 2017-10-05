# encoding: utf-8
#

from osgeo import ogr

def Geo2Grid (location,dimensions,resolution,extent):
    """
    Função que indica em qual linha e coluna um ponto geográfico se encontra
    considerando que a grade se inicia no canto superior esquerdo

    Parametros:
    :param location (Geometry):
    :param dimensions (dict):
    :param resoution (Dict):
    :param extent (Dict):
    :return: (int,int) - retorna o numero da linha e da coluna
    """
    x = location.GetX()
    y = location.GetY()

    col = int((x-extent['xmin'])/resolution['x'])
    row = int(dimensions['rows']-((y-extent['ymin'])/resolution['y']))

    return col,row