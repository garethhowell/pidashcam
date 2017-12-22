
"""A Raspberry Pi dashboard camera

See https://www.github.com/garethhowell/pidashcam
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

def readme():
    with open('README.rst') as f:
        return f.read()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name='pidashcam',

	version ='1.0.0',

	description = 'A Raspberry Pi dashboard camera',
	long_description = readme(),

	# The project's homepage
	url = 'https://www.github.com/garethhowell/pidashcam',

	# Author details
	author = 'Gareth Howell',
	author_email = 'gareth.howell@gmail.com',

	# license
	license = 'GPL3',

	classifiers = [
		# How mature is this project? Common values are
    	#   3 - Alpha
    	#   4 - Beta
    	#   5 - Production/Stable
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Other Audience',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Other/Nonlisted Topic'
	],

	keywords = 'dashcam raspbian python RaspberryPi',

	# You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

	data_files = [
		('/etc/default', ['default/pidashcam']),
		('/etc/systemd/system', ['systemd/pidashcam.service'])
	],

    scripts = [
        'scripts/pidashcam'
    ]
)
