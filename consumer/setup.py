from setuptools import setup, find_packages

setup(name='twnews_consumer',
      packages=find_packages(),
      entry_points = {
        'console_scripts': [
            'twnews_consumer = twnews_consumer.main:main',
        ]
      },
      #install_requires=['antlr4-python2-runtime'],
      zip_safe=False)