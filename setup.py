from setuptools import setup, find_packages

setup(name='pyy_chr',
      version='0.0',
      description='pyy_chr',
      url='https://github.com/nleseul/pyy_chr',
      author='NLeseul',
      license='Unlicense',
      packages=find_packages(),
      install_requires=[
          'events',
          'Pillow'
      ],
      extras_require={
          'ui-kivy': [
              'kivy'
          ]
      },
      zip_safe=False)
