from setuptools import setup

name = 'cdeps'
version = '0.1.3'

setup(name=name,
      version=version,
      description='Generates c file dependencies',
      author='Per Forser',
      py_modules=[
          'cdeps',
      ],
      entry_points={
          'console_scripts': [
              'cdeps=cdeps:main',
          ],
      }
      )

