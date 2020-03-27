from setuptools import setup

setup(name='coviduci',
      version='0.1',
      description='Aplicacion COVIDUCI-EC',
      license='Apache',
      packages=['coviduci'],
      zip_safe=False,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.env"]
        }
      )
