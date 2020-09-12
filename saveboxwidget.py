from pathlib import Path
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from ui_components.saveboxwidget_ui import Ui_SaveBoxWidget
from enum import Enum
import h5py


class Mode(Enum):
    SINGLE = 0
    ABSORPTION = 1
    FLUORESCENCE = 2


class SaveBoxWidget(QWidget, Ui_SaveBoxWidget):
    save_request_signal  = pyqtSignal()

    def __init__(self, parent=None):
        super(SaveBoxWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.data_root = ''
        self.run_name = ''
        self.camera_name = ''
        self.file_number = ''
        self.file_suffix = '.h5'
        self.file_name = ''
        self.save_path = None
        self.file_path = None

        self.mode = Mode.SINGLE

    def get_savepath(self):
        self.data_root = self.data_root_lineEdit.text()
        self.run_name = self.run_name_lineEdit.text()
        self.camera_name = self.camera_name_lineEdit.text()
        self.file_number = self.file_number_spinBox.text()
        self.file_suffix = '.h5'

        self.save_path = Path(self.data_root, self.run_name, self.camera_name)
        self.file_name = f'jkam_capture_{self.file_number:05d}{self.file_suffix}'
        self.file_path = Path(self.save_path, self.file_name)

    def toggle_enable_editing(self, toggle_value):
        self.data_root_lineEdit.setEnabled(toggle_value)
        self.run_name_lineEdit.setEnabled(toggle_value)
        self.camera_name_lineEdit.setEnabled(toggle_value)
        self.file_number_spinBox.setEnabled(toggle_value)

    def save(self, *args):
        self.get_savepath()
        if self.mode == Mode.SINGLE:
            self.save_h5_single(*args)

    def save_h5_single(self, frame, timestamp=None):
        with h5py.File(self.file_path, 'w') as hf:
            hf.create_dataset("frame", data=frame.astype('uint16'))
            hf.attrs['timestamp'] = timestamp.isoformat()
