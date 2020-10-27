import datetime
from pathlib import Path
from enum import Enum
import h5py
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from package.ui.saveboxwidget_ui import Ui_SaveBoxWidget


class SaveBoxWidget(QWidget, Ui_SaveBoxWidget):
    # default_root = Path.cwd()
    default_root = Path('Y:/', 'expdata-e6', 'data')
    default_camera_name = 'jkam_imaging'

    class ModeType(Enum):
        SINGLE = 0
        ABSORPTION = 1
        FLUORESCENCE = 2
        MULTISHOT = 3

    def __init__(self, parent=None):
        super(SaveBoxWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.data_root_path = self.default_root
        data_root_string = get_abbreviated_path_string(self.data_root_path, max_len=30)
        self.data_root_value_label.setText(data_root_string)
        self.daily_data_path = Path('')
        self.run_path = Path('')
        self.data_path = Path('')
        self.imaging_system_path = Path('')
        self.file_path = Path('')
        self.file_number = 1
        self.file_prefix = ''
        self.file_suffix = '.h5'
        self.file_name = ''
        self.imaging_system = None

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
        self.disarm()

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
        self.daily_path_value_label.setText(str(self.daily_data_path))

    def set_run_path(self):
        if self.run_path != Path(self.run_name_lineEdit.text()):
            self.run_path = Path(self.run_name_lineEdit.text())
            self.file_number_spinBox.setValue(0)
            self.file_number = self.file_number_spinBox.value()

    def build_data_path(self):
        self.set_daily_data_path()
        self.set_run_path()
        self.data_path = Path(self.data_root_path, self.daily_data_path, self.run_path, self.imaging_system_path)
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
                try:
                    self.data_path.mkdir(parents=True)
                except FileNotFoundError as e:
                    print(e)
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
        if self.tabWidget.currentIndex() == 0 and not self.autosaving:
            self.build_data_path()
        self.build_file_name()
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
        if self.mode == self.ModeType.MULTISHOT:
            self.save_h5_multishot_frames(*args)
        self.increment_file_number()

    def save_h5_single_frame(self, frame_dict):
        if frame_dict is not None:
            with h5py.File(str(self.file_path), 'w') as hf:
                hf.create_dataset('frame', data=frame_dict['frame'].astype('uint16'))
                for key, value in frame_dict['metadata'].items():
                    hf['frame'].attrs[key] = value

    def save_h5_absorption_frames(self, atom_frame_dict, bright_frame_dict, dark_frame_dict):
        frames_dict = {'atom_frame': atom_frame_dict,
                       'bright_frame': bright_frame_dict,
                       'dark_frame': dark_frame_dict}
        with h5py.File(str(self.file_path), 'w') as hf:
            for frame_name, frame_dict in frames_dict.items():
                hf.create_dataset(frame_name, data=frame_dict['frame'].astype('uint16'))
                for key, value in frame_dict['metadata'].items():
                    hf[frame_name].attrs[key] = value

    def save_h5_fluorescence_frames(self, atom_frame_dict, reference_frame_dict):
        frames_dict = {'atom_frame': atom_frame_dict,
                       'reference_frame': reference_frame_dict}
        with h5py.File(str(self.file_path), 'w') as hf:
            for frame_name, frame_dict in frames_dict.items():
                hf.create_dataset(frame_name, data=frame_dict['frame'].astype('uint16'))
                for key, value in frame_dict['metadata'].items():
                    hf[frame_name].attrs[key] = value

    def save_h5_multishot_frames(self, frame_dict_list):
        with h5py.File(str(self.file_path), 'w') as hf:
            for idx, frame_dict in enumerate(frame_dict_list):
                frame_name = f'frame-{idx:02d}'
                hf.create_dataset(frame_name, data=frame_dict['frame'].astype('uint16'))
                for key, value in frame_dict['metadata'].items():
                    hf[frame_name].attrs[key] = value

    def arm(self, imaging_system):
        self.save_single_pushButton.setEnabled(True)
        self.run_pushButton.setEnabled(True)
        self.imaging_system = imaging_system
        imaging_system_name = imaging_system.name
        self.imaging_system_path = Path(imaging_system_name)
        self.imaging_system_value_label.setText(imaging_system_name)
        if self.tabWidget.currentIndex() == 0:
            self.build_data_path()
        self.build_file_name()

    def disarm(self):
        self.save_single_pushButton.setEnabled(False)
        self.run_pushButton.setEnabled(False)
        self.imaging_system = None
        self.imaging_system_path = Path('')
        self.imaging_system_value_label.setText('')


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
