from setuptools import setup

setup(
    name='landsat_prep',
    version='0.0.1',
    description='Landsat prep tools',
    url='git@github.com:heatherbaier/landsat-imagery-prep.git',
    author='Heather Baier',
    author_email='hmbaier@email.wm.edu',
    license='unlicense',
    packages=['landsat_prep'],
    install_requires = ["earthengine-api", "rasterio", "torchvision", "joblib", "geopandas"],
    zip_safe=False
)