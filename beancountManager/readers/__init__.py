import os  # get all contained scripts
import importlib  # import these scripts and get the contained classes
import sys  # set these classes as attributes of this module

thisModule = sys.modules[__name__]

path = os.path.dirname(os.path.realpath(__file__))
folder_content = os.listdir(path)

all_py_scripts = []
for content in folder_content:
    if content[-3:] == '.py' and '__' not in content and 'base' not in content and 'default' not in content:
        all_py_scripts.append(content)

options = []

for script in all_py_scripts:

    name = script.split('_')[0].title()
    module = importlib.import_module('.'+script[:-3],
                                     package='beancountManager.readers')
    reader = getattr(module, '{}Converter'.format(name))

    setattr(thisModule, name, reader)
    options.append(name)
