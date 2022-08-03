import setuptools

setuptools.setup(
    name="arglite",
    version="0.1",
    packages=['arglite'],
    package_dir={'arglite': 'src'},
    include_package_data=True,
    description='A lightweight, dynamic arg parser for fun, but not profit.',
    long_description=open('README.md', 'r').read(),
    install_requires=[line.strip() for line in open('requirements.txt', 'r').readlines()]
 )
