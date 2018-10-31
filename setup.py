import os, sys
try:
    from setuptools import setup, find_packages
    use_setuptools = True
except ImportError:
    from distutils.core import setup
    use_setuptools = False

try:
    with open('README.md', 'rt') as readme:
        description = '\n' + readme.read()
except IOError:
    # maybe running setup.py from some other dir
    description = ''

python_requires='>=3.5'
install_requires = [
    'rx>=1.6',
    'cyclotron>=0.4',
    'aiohttp>=3.0',
]

setup(
    name="cyclotron-aio",
    version='0.6.0',
    url='https://github.com/MainRo/cyclotron-aio.git',
    license='MIT',
    description="Asynchronous IO drivers for cyclotron",
    long_description=description,
    author='Romain Picard',
    author_email='romain.picard@oakbits.com',
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ]
)
