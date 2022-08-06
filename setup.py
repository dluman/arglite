import setuptools

setuptools.setup(
    name="arglite",
    version="0.2",
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

Installation
============

Find this tool on `PyPI`: `pip install arglite`

Usage
=====

Check this out:

import arglite

def main():
  print(arglite.parser.a)
  print(arglite.parser.b)
  print(arglite.parser.c)

  arglite.parser.display()

if __name__ == "__main__":
  main()

Run using: python main.py -a Yo --b that is -c.

Notes
=====
No automatic `-h` flag yet; soon?
Flags with no value are automatically converted to `True` boolean
The module uses `ast.literal_eval`, so `"{'a':'b'}"` will convert to a `dict` (all quotes required)    
    """,
    long_description_content_type="text/x-rst",
    install_requires=[
      'rich',
    ]
 )
