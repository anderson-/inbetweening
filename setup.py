import os
from setuptools import setup

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'freecad', 'i10g', 'version.py')
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.i10g',
      version=str(__version__),
      packages=['freecad',
                'freecad.i10g'],
      maintainer='Anderson Antunes',
      maintainer_email='anderson.utf@gmail.com',
      url='https://github.com/anderson-/inbetweening',
      description='FreeCAD Simple Animation Workbench',
      install_requires=['numpy'],
      include_package_data=True)
