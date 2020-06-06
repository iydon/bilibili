'''Set up package bilibili-utils.
'''
import setuptools


with open('README.md', 'r') as f:
	long_description = f.read()

setuptools.setup(
	name='bilibili-utils',
	version='0.1',
	author='Iydon Liang',
	author_email='liangiydon@gmail.com',
	license='MIT License',
	description='Bilibili Utilities',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Iydon/bilibili-utils',
	packages=setuptools.find_packages(),
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.6',
	install_requires=[
		'selenium',
		'tqdm',
		'requests',
		'faker',
		'matplotlib',
		'aiohttp',
		'sqlalchemy',
		'lxml',
		'bs4',
		'rsa',
		'pymusic-dl',
		'fuzzywuzzy',
		'retrying',
		'pyexecjs',
		'langid',
	],
	tests_require=[],
)
