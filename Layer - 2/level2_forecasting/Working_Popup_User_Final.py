from PyQt5.QtGui import *
from PyQt5.QtWidgets import QHBoxLayout, QDockWidget, QWidget
from osgeo import gdal
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.PyQt.QtGui import (
    QColor,
)

from qgis.PyQt.QtCore import Qt, QRectF

from qgis.core import (
    QgsVectorLayer,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsGeometry,
    QgsMapRendererJob,
)

from qgis.gui import (
    QgsMapCanvas,
    QgsVertexMarker,
    QgsMapCanvasItem,
    QgsRubberBand,
)

class MyWnd(QMainWindow):
    def __init__(self, layer):
        QMainWindow.__init__(self)
        self.canvas = QgsMapCanvas()
        self.canvas.show()
        self.canvas.enableAntiAliasing(True)
        self.canvas.setCanvasColor(Qt.white)
        
        #urlWithParams = 'url=https://sedac.ciesin.columbia.edu:443/geoserver/ows?SERVICE=WMS&layers=ipcc:ipcc-synthetic-vulnerability-climate-2005-2050-2100&format=image/png&crs=EPSG:4326&styles='
        #urlWithParams = 'url=https://sedac.ciesin.columbia.edu:443/geoserver/ows?SERVICE=WMS&layers=cartographic:national-boundaries&format=image/png&crs=EPSG:4326&styles='
        urlWithParams = 'url=https://sedac.ciesin.columbia.edu:443/geoserver/ows?SERVICE=WMS&layers=other:srtm-elevation-above-sea-level_1km&format=image/png&crs=EPSG:4326&styles='
        self.layer = QgsRasterLayer(urlWithParams, 'Climate Vulnerability', 'wms')
        if not self.layer.isValid():
          print("Layer failed to load!")
        
      #  path_to_ports_layer = "C:/Users/shara/Desktop/Final_Results/User_Scenario.shp"
      #  self.layer = QgsVectorLayer(path_to_ports_layer, "User Scenario", "ogr")
      #  if not self.layer.isValid():
      #      print("Layer failed to load!")
        #self.layer = QgsVectorLayer("C:/Users/shara/Desktop/Final_Results/User_Scenario.shp","ogr")
        #QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        #QgsProject.instance().addMapLayer(self.layer)

        self.canvas.setExtent(self.layer.extent())
        self.canvas.setLayers([self.layer])
        self.setCentralWidget(self.canvas)
        
        self.actionPoly = QAction("Draw Rectangle", self)
        self.actionZoomIn = QAction("Zoom in", self)
        self.actionZoomOut = QAction("Zoom out", self)
        self.actionPan = QAction("Pan", self)
        self.actionPoly.setCheckable(True)
        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)
        self.actionPoly.triggered.connect(self.poly)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionPan.triggered.connect(self.pan)
        self.toolbar = self.addToolBar("Canvas actions")
        self.toolbar.addAction(self.actionPoly)
        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)
        
        self.toolPoly = RectangleMapTool(self.canvas)
        self.toolPoly.setAction(self.actionPoly)
        
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolZoomOut.setAction(self.actionZoomOut)
        self.pan()
    
    def poly(self):
        self.canvas.setMapTool(self.toolPoly)
    
    def zoomIn(self):
        self.canvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        self.canvas.setMapTool(self.toolPan)


class RectangleMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset()

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            print("Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum())

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset()
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
        point1 = QgsPoint(startPoint.x(), startPoint.y())
        point2 = QgsPoint(startPoint.x(), endPoint.y())
        point3 = QgsPoint(endPoint.x(), endPoint.y())
        point4 = QgsPoint(endPoint.x(), startPoint.y())

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)    # true to update canvas
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif (self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y()):
            return None
        return QgsRectangle(self.startPoint, self.endPoint)

    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.deactivated.emit()