import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ImageViewer(QGraphicsView):
    """Image Viewer widget for a QPixmap in a QGraphicsView scene that displays a converted QPixmap image
    Allows the user to zoom and pan an image with the mouse
    """

    def __init__(self, parent):

        super(ImageViewer, self).__init__()

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Initialize a local handle for the scene's current image
        self._pixmap_handle = None

        # List of QRectF zoom boxes in scene pixel coordinates
        self.zoom_list = list()

        # Flags for enabling or disabling mouse interaction
        self.zoom_flag = True
        self.pan_flag = True

    def set_image(self, image):
        """Set the scene's current image pixmap to the input QImage or QPixmap"""

        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.set_image: Argument must be a QImage or QPixmap.")

        if self._pixmap_handle is not None:
            self._pixmap_handle.setPixmap(pixmap)
        else:
            self._pixmap_handle = self.scene.addPixmap(pixmap)

        # Set the scene size to the image's size
        self.setSceneRect(QRectF(pixmap.rect()))

        # Update the viewer
        self.update_viewer()

    def remove_image(self):
        """Removes the current image from the scene if it exists"""

        if self._pixmap_handle is not None:
            self.scene.removeItem(self._pixmap_handle)
            self._pixmap_handle = None

    def update_viewer(self):
        """Update the image viewer with the image, taking into account aspect ratio and zoom options"""

        if self._pixmap_handle and len(self.zoom_list) and self.sceneRect().contains(self.zoom_list[-1]):
            self.fitInView(self.zoom_list[-1], Qt.IgnoreAspectRatio)
        else:
            # Clear the list of zoom boxes
            self.zoom_list = list()
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """Maintain current zoom and aspect ratio on resize of the window"""
        self.update_viewer()

    def mousePressEvent(self, event):
        """"""

        if event.button() == Qt.LeftButton:
            if self.pan_flag:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        elif event.button() == Qt.RightButton:
            if self.zoom_flag:
                self.setDragMode(QGraphicsView.RubberBandDrag)
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):

        QGraphicsView.mouseReleaseEvent(self, event)

        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
        elif event.button() == Qt.RightButton:
            if self.zoom_flag:
                viewBBox = self.zoom_list[-1] if len(self.zoom_list) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoom_list.append(selectionBBox)
                    self.update_viewer()
            self.setDragMode(QGraphicsView.NoDrag)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.zoom_flag:
                self.zoom_list = list()
                self.update_viewer()
        QGraphicsView.mouseDoubleClickEvent(self, event)