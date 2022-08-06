import setuptools

setuptools.setup(
    name="arglite",
    version="0.1",
    packages=['arglite'],
    package_dir={'arglite': 'src'},
    include_package_data=True,
    description="A lightweight, dynamic arg parser for fun, but not profit.",
    long_description="A  l i g h t w e i g h t ,  d y n a m i c   a r g   p a r s e r   f o r   f u n,  b u t   n o t   p r o f i t.",
    long_description_content_type="text/x-rst",
    install_requires=[
      'rich',
    ]
 )
