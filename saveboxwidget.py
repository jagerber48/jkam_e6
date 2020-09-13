import datetime
from pathlib import Path
from enum import Enum
import h5py

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSignal

from ui_components.saveboxwidget_ui import Ui_SaveBoxWidget


class Mode(Enum):
    SINGLE = 0
    ABSORPTION = 1
    FLUORESCENCE = 2


class SaveBoxWidget(QWidget, Ui_SaveBoxWidget):
    save_request_signal = pyqtSignal()
    default_root = Path.cwd()
    # default_root = Path('Y:/', 'expdata-e6', 'data', '2020', '09', '12', 'data')
    default_camera_name = 'jkam_imaging'

    def __init__(self, parent=None):
        super(SaveBoxWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.data_root_path = self.default_root
        data_root_string = get_abbreviated_path_string(self.data_root_path, max_len=30)
        self.data_root_value_label.setText(data_root_string)
        self.daily_data_path = None
        self.run_path = None
        self.data_path = None
        self.file_path = None
        self.file_number = 1
        self.file_prefix = ''
        self.file_suffix = '.h5'
        self.file_name = ''

        self.mode = Mode.SINGLE

        self.data_root_pushButton.clicked.connect(self.select_data_root)
        self.run_name_lineEdit.editingFinished.connect(self.build_data_path)
        self.select_data_pushButton.clicked.connect(self.select_data_path)

        self.file_prefix_lineEdit.editingFinished.connect(self.build_file_name)
        self.file_number_spinBox.editingFinished.connect(self.build_file_name)
        self.file_number_spinBox.valueChanged.connect(self.build_file_name)

        self.set_daily_data_path()
        self.set_run_path()
        self.build_data_path()
        self.build_file_name()
        self.set_file_path()

    def select_data_root(self):
        selected_directory = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.data_root_path = Path(selected_directory)
        data_root_string = get_abbreviated_path_string(self.data_root_path, max_len=30)
        self.data_root_value_label.setText(data_root_string)
        self.build_data_path()

    def set_daily_data_path(self):
        """
        Return folder path in the format 'YYYY\\MM\\DD\\data\\'
        """
        today = datetime.datetime.today()
        year = f'{today.year:4d}'
        month = f'{today.month:02d}'
        day = f'{today.day:02d}'
        self.daily_data_path = Path(year, month, day, 'data')

    def set_run_path(self):
        self.run_path = Path(self.run_name_lineEdit.text())

    def build_data_path(self):
        self.set_daily_data_path()
        self.set_run_path()
        self.data_path = Path(self.data_root_path, self.daily_data_path, self.run_path)
        data_dir_label_string = get_abbreviated_path_string(self.data_path)
        self.data_dir_label.setText(data_dir_label_string)
        self.set_file_path()

    def select_data_path(self):
        selected_directory = QFileDialog.getExistingDirectory(None, "Select Directory")
        self.data_path = Path(selected_directory)
        data_dir_label_string = get_abbreviated_path_string(self.data_path)
        self.data_dir_label.setText(data_dir_label_string)
        self.set_file_path()

    def build_file_name(self):
        self.file_prefix = self.file_prefix_lineEdit.text()
        self.file_number = self.file_number_spinBox.value()
        self.file_suffix = '.h5'
        self.file_name = f'{self.file_prefix}_{self.file_number:05d}{self.file_suffix}'
        self.file_path_label.setText(f'Next File Name: {self.file_name}')
        self.set_file_path()

    def set_file_path(self):
        self.file_path = Path(self.data_path, self.file_name)

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
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True)
        with h5py.File(self.file_name, 'w') as hf:
            hf.create_dataset("frame", data=frame.astype('uint16'))
            if timestamp is not None:
                hf.attrs['timestamp'] = timestamp.isoformat()


def get_abbreviated_path_string(path, max_len=50):
    parts = path.parts
    path_string = ''
    path_abbreviated = False
    for ind in range(len(parts)):
        path_string = '\\'.join(parts[ind:])
        if len(path_string) <= max_len:
            break
        path_abbreviated = True
    if path_abbreviated:
        return f'...\\{path_string}\\'
    else:
        return path_string

