from setuptools import setup, find_packages
import os
import distutils.core 

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='OpenFruitAPI',
    version='0.1dev',
    packages=find_packages(),
    license='License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    long_description=open('README.md').read(),

)

