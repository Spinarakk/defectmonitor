class PreCapture(QThread):
    """Part Slice Convertor:

    Converts the .cls files into ASCII format that the rest of the program can interpret.
    """

    def __init__(self, cls_folder):
        QThread.__init__(self)
        self.cls_folder = cls_folder
        self.file_list = os.listdir(self.cls_folder)
        self.file_dictionary = dict()

class Capture():
    pass