import os
from pathlib import Path

cwd_path = Path.cwd()
ui_resource_path = Path(cwd_path, 'ui_resources')

ui_file_paths = list(Path(ui_resource_path).glob('*.ui'))
input_names = []
output_names = []
for path in ui_file_paths:
    name = path.name
    convert_input_string = str(Path('ui_resources', name))
    py_name = str(Path(name).with_suffix('')) + '_ui.py'
    convert_output_string = str(Path('package', 'ui', py_name))
    input_names.append(convert_input_string)
    output_names.append(convert_output_string)
    os.system(f'python -m PyQt5.uic.pyuic -x {convert_input_string} -o {convert_output_string}')
print(input_names)
print(output_names)