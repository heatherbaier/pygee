from setuptools import setup

setup(
    name='pygee',
    version='0.0.1',
    description='Landsat prep tools',
    url='git@github.com:heatherbaier/landsat-imagery-prep.git',
    author='Heather Baier',
    author_email='hmbaier@email.wm.edu',
    license='unlicense',
    packages=['pygee'],
    install_requires = ["rasterio", "torchvision", "joblib", "geopandas"],
    zip_safe=False
)
