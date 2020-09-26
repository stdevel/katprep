"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='katprep',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.5.0',
    description='Python toolkit for automating system maintenance and generating patch reports along with '
                'Foreman/Katello and Red Hat Satellite 6.x',
    long_description=long_description,
    url='https://github.com/stdevel/katprep',
    author='Christian Stankowic',
    author_email='katprep@st-devel.net',

    # Choose your license
    license='GPLv3',

    # Add classifier https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='foreman katello linux redhat centos satellite6 satellite fedora maintenance maintenance-tasks '
             'maintenance-reports iso27001',
    packages=find_packages(exclude=['doc', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'lxml',
        'pyvmomi',
        'pyyaml',
        'fernet',
        'cryptography',
        # TODO: specify libvirt?
    ],
    # Remember to insert the requirements into requirements.txt!

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        # 'dev': ['check-manifest'],
        'test': ['pytest', 'codecov'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #    'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # TODO: add config.yml later
    data_files=[('etc/katprep/', ['templates/template.html', 'templates/template.md'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
           'katprep_authconfig=katprep.authconfig:cli',
           'katprep_maintenance=katprep.maintenance:cli',
           'katprep_parameters=katprep.parameters:cli',
           'katprep_populate=katprep.populate:cli',
           'katprep_report=katprep.report:cli',
           'katprep_snapshot=katprep.snapshot:cli',
        ],
    },
)
