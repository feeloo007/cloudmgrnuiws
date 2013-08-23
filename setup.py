VERSION = '0.0.1'

from setuptools import setup, find_packages

setup(
      name = 'cloudmgrnuiws',
      version = VERSION,
      author = '',
      author_email = '',
      description = '',
      license = '',
      keywords = '',
      url = '',
      packages = find_packages(),
      include_package_data = True,
      package_data = {'' : ['*.cfg']},
      zip_safe = False,
      install_requires = (
	'nagare==0.4.1',
	'plone.synchronize==1.0.1',
	'pyinotify==0.9.4',
      ),
      message_extractors = { 'cloudmgrnuiws' : [('**.py', 'python', None)] },
      entry_points = """
      [nagare.applications]
      cloudmgrnuiws = cloudmgrnuiws.app:app
      """
     )

