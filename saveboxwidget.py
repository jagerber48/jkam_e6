import datetime
from pathlib import Path
from enum import Enum
import h5py
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from ui_components.saveboxwidget_ui import Ui_SaveBoxWidget


class SaveBoxWidget(QWidget, Ui_SaveBoxWidget):
    # default_root = Path.cwd()
    default_root = Path('Y:/', 'expdata-e6', 'data')
    default_camera_name = 'jkam_imaging'

    class ModeType(Enum):
        SINGLE = 0
        ABSORPTION = 1
        FLUORESCENCE = 2

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

        self.mode = self.ModeType.SINGLE
        self.autosaving = False

        self.data_root_pushButton.clicked.connect(self.select_data_root)
        self.run_name_lineEdit.editingFinished.connect(self.build_data_path)
        self.select_data_pushButton.clicked.connect(self.select_data_path)

        self.file_prefix_lineEdit.editingFinished.connect(self.build_file_name)
        self.file_number_spinBox.editingFinished.connect(self.build_file_name)
        self.file_number_spinBox.valueChanged.connect(self.build_file_name)

        self.run_pushButton.clicked.connect(self.toggle_autosave)

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
        self.data_root_pushButton.setEnabled(toggle_value)
        self.run_name_lineEdit.setEnabled(toggle_value)
        self.file_prefix_lineEdit.setEnabled(toggle_value)
        self.file_number_spinBox.setEnabled(toggle_value)
        self.select_data_pushButton.setEnabled(toggle_value)
        self.save_single_pushButton.setEnabled(toggle_value)

    def toggle_autosave(self):
        if self.run_pushButton.isChecked():
            if self.data_path.exists():
                msg = "The target run folder already exists, proceeding may overwrite existing data, continue?"
                reply = QMessageBox.question(self, 'Overwrite confirmation',
                                             msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    print('Continuous save initialization aborted')
                    self.run_pushButton.setChecked(False)
                    return
            elif not self.data_path.exists():
                self.data_path.mkdir(parents=True)
            self.toggle_enable_editing(False)
            self.run_pushButton.setText('Stop Run')
            self.autosaving = True
        elif not self.run_pushButton.isChecked():
            self.toggle_enable_editing(True)
            self.run_pushButton.setText('Start Run')
            self.autosaving = False

    def increment_file_number(self):
        self.file_number += 1
        self.file_number_spinBox.setValue(self.file_number)
        self.build_file_name()
        self.set_file_path()

    def save(self, *args):
        # Only verify file path existence for single shot saves. For autosaving the path is verified when the
        # run is started.
        if not self.autosaving:
            if self.file_path.exists():
                msg = "The target file already exists, overwrite?"
                reply = QMessageBox.question(self, 'Overwrite confirmation',
                                             msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    print('Save operation aborted')
                    # self.scan_button.setChecked(False)
                    return
            if not self.data_path.exists():
                self.data_path.mkdir(parents=True)
        if self.mode == self.ModeType.SINGLE:
            self.save_h5_single_frame(*args)
        if self.mode == self.ModeType.ABSORPTION:
            self.save_h5_absorption_frames(*args)
        if self.mode == self.ModeType.FLUORESCENCE:
            self.save_h5_fluorescence_frames(*args)
        self.increment_file_number()

    def save_h5_single_frame(self, frame, timestamp=None):
        with h5py.File(str(self.file_path), 'w') as hf:
            hf.create_dataset("frame", data=frame.astype('uint16'))
            if timestamp is not None:
                hf.attrs['timestamp'] = timestamp.isoformat()

    def save_h5_absorption_frames(self, atom_frame, bright_frame, dark_frame, timestamp=None):
        with h5py.File(str(self.file_path), 'w') as hf:
            hf.create_dataset("atom_frame", data=atom_frame.astype('uint16'))
            hf.create_dataset("bright_frame", data=bright_frame.astype('uint16'))
            hf.create_dataset("dark_frame", data=dark_frame.astype('uint16'))
            if timestamp is not None:
                hf.attrs['timestamp'] = timestamp.isoformat()

    def save_h5_fluorescence_frames(self, atom_frame, reference_frame, timestamp=None):
        with h5py.File(str(self.file_path), 'w') as hf:
            hf.create_dataset("atom_frame", data=atom_frame.astype('uint16'))
            hf.create_dataset("reference_frame", data=reference_frame.astype('uint16'))
            if timestamp is not None:
                hf.attrs['timestamp'] = timestamp.isoformat()


def get_abbreviated_path_string(path, max_len=50):
    """
    Abbreviates string representation of a path object by removing top directory ancestors until the
    string representation is less than max_len. Returns the string representation
    """
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
