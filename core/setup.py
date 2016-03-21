from setuptools import setup, find_packages

setup(name='twnews',
      packages=find_packages(),
      entry_points = {
        'console_scripts': [
            'twnews = twnews.main:main',
        ]
      },
      #install_requires=['feedparser'],
      zip_safe=False)
