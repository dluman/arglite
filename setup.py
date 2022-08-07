import setuptools

setuptools.setup(
    name="arglite",
    version="0.3.5",
    packages=['arglite'],
    package_dir={'arglite': 'src'},
    include_package_data=True,
    description="A lightweight, dynamic arg parser for fun, but not profit.",
    long_description="""
=======
arglite
=======

A lightweight, dynamic argument parsing library for Python programs with klugy support for typing variables.

I made this for a teaching machine project I'm working on (I needed a custom argument parser for _reasons_),
and I'm always too impatient to use `argparse`.

Notes
=====
Flags with no value are automatically converted to `True` boolean
The module uses `ast.literal_eval`, so `"{'a':'b'}"` will convert to a `dict` (all quotes required)    
Programs will produce error messages when flags are missing
    """,
    long_description_content_type="text/x-rst",
    install_requires=[
      'rich',
    ],
    url="https://github.com/dluman/arglite"
 )
