from pathlib import Path
from enum import Enum
import h5py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from ui_components.saveboxwidget_ui import Ui_SaveBoxWidget


class Mode(Enum):
    SINGLE = 0
    ABSORPTION = 1
    FLUORESCENCE = 2


class SaveBoxWidget(QWidget, Ui_SaveBoxWidget):
    save_request_signal = pyqtSignal()
    default_root = Path('Y:/', 'expdata-e6', 'data', '2020', '09', '12', 'data')
    default_camera_name = 'jkam_imaging'

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

        self.set_save_path_pushButton.clicked.connect(self.get_savepath)
        self.autofill_pushButton.clicked.connect(self.autofill_path)

    def get_savepath(self):
        self.data_root = self.data_root_lineEdit.text()
        self.run_name = self.run_name_lineEdit.text()
        self.camera_name = self.camera_name_lineEdit.text()
        self.file_number = int(self.file_number_spinBox.text())
        self.file_suffix = '.h5'

        self.save_path = Path(self.data_root, self.run_name, self.camera_name)
        self.file_name = f'jkam_capture_{self.file_number:05d}{self.file_suffix}'
        self.file_path = Path(self.save_path, self.file_name)
        self.file_path_label.setText(str(self.file_path))

    def autofill_path(self):
        self.data_root = str(self.default_root)
        self.data_root_lineEdit.setText(self.data_root)
        found_new_run_name = False
        run_number = 1
        run_dir = ''
        while not found_new_run_name:
            run_dir = f'run{run_number:d}'
            if Path(self.data_root, run_dir).is_dir():
                run_number += 1
            else:
                found_new_run_name = True
        self.run_name = run_dir
        self.run_name_lineEdit.setText(self.run_name)
        self.camera_name = self.default_camera_name
        self.camera_name_lineEdit.setText(self.camera_name)
        self.file_suffix = '.h5'

        self.save_path = Path(self.data_root, self.run_name, self.camera_name)

        found_new_file_number = False
        file_number = 1
        while not found_new_file_number:
            file_name = f'jkam_capture_{file_number:05d}{self.file_suffix}'
            file_path = Path(self.save_path, file_name)
            if file_path.is_file():
                file_number += 1
            else:
                found_new_file_number = True
        self.file_number = file_number
        self.file_number_spinBox.setValue(self.file_number)
        self.file_name = f'jkam_capture_{self.file_number:05d}{self.file_suffix}'
        self.file_path = Path(self.save_path, self.file_name)
        self.file_path_label.setText(str(self.file_path))

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
