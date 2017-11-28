
"""pidashcam: PiDashCam dashcam daemon

This script is intended for use with the PiDashCam on a Raspberry Pi computer.
"""

classifiers = """\
Development Status :: 5 - Testing/Beta
Intended Audience :: developers
License :: GNU General Public License Version 3
Programming Language :: Python >= 2.7
Topic :: PiDashCam
Topic :: PiDashCam dashcam daemon
Operating System :: Linux (Raspbian)
"""


from distutils.core import setup

doclines = __doc__.split("\n")



datafiles=[
	('/etc/default', ['default/pidashcam']),
	('/etc/systemd/services', ['systemd/pidashcam'])
]

setup(name='pidashcam',
      version='0.1dev',
      description=doclines[0],
      long_description = "\n".join(doclines[2:]),
      license='GPL3',
      author='Gareth Howell',
      author_email='gareth.howell@gmail.com',
      url='http://garethhowell.com',
      platforms=['POSIX'],
      classifiers = filter(None, classifiers.split("\n")),
      scripts=['scripts/pidashcam'],
      data_files = datafiles
      )
