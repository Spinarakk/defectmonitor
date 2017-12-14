# Import PyQt modules
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ImageViewer(QGraphicsView):
    """Image Viewer widget for a QPixmap in a QGraphicsView scene that displays a converted QPixmap image
    Allows the user to zoom and pan an image with the mouse
    """

    # Signal that will be emitted after the zoom in action has been completed
    # Just used to toggle the Zoom In action unchecked
    zoom_done = pyqtSignal()
    mouse_pos = pyqtSignal(int, int)

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
        self.zoom_flag = False

    def set_image(self, image):
        """Set the scene's current image to the received image after converting it to QPixmap"""

        # Convert the received image into a QPixmap that can be displayed on the graphics viewer
        qimage = QImage(image.data, image.shape[1], image.shape[0], 3 * image.shape[1], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        if self._pixmap_handle is not None:
            self._pixmap_handle.setPixmap(pixmap)
        else:
            self._pixmap_handle = self.scene.addPixmap(pixmap)

        # Set the scene size to the image's size
        self.setSceneRect(QRectF(pixmap.rect()))

        # Update the viewer
        self.update_viewer()

    def reset_image(self):
        """Reset the image back to its original state (no zoom or pan)"""
        self.zoom_list = list()
        self.update_viewer()
        self.setDragMode(QGraphicsView.NoDrag)

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
        """When the Left Mouse button is held down, allow the user to set a zoom box"""

        if event.button() == Qt.LeftButton:
            if self.zoom_flag:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            elif self.zoom_list:
                self.setDragMode(QGraphicsView.ScrollHandDrag)

        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """When the Left Mouse button is released after being held down, zoom to the set zoom box area"""

        QGraphicsView.mouseReleaseEvent(self, event)

        if event.button() == Qt.LeftButton and self.zoom_flag:
            view_box = self.zoom_list[-1] if len(self.zoom_list) else self.sceneRect()
            selection_box = self.scene.selectionArea().boundingRect().intersected(view_box)
            self.scene.setSelectionArea(QPainterPath())
            if selection_box.isValid() and (selection_box != view_box):
                self.zoom_list.append(selection_box)
                self.update_viewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.zoom_done.emit()

    def mouseDoubleClickEvent(self, event):
        """When the Left Mouse button is double clicked, reset the zoom back to the original size"""

        if event.button() == Qt.LeftButton:
            self.reset_image()

        QGraphicsView.mouseDoubleClickEvent(self, event)

    def mouseMoveEvent(self, event):
        """When the mouse cursor is moved over the graphics view, the position of the cursor within the graphics view
        Will be emitted back to the dialog box if mouseTracking is enabled on the graphics view in question"""

        # Convert the mouse position from being relative to the window to being relative to the image resolution
        pos = self.mapToScene(event.pos())
        self.mouse_pos.emit(round(pos.x()), round(pos.y()))

        QGraphicsView.mouseMoveEvent(self, event)
