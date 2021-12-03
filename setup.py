from setuptools import find_packages, setup

_requirements = {
    "client": ["grpcio", "numpy", "python-lzo", "xarray"],
    "server": ["grpcio", "napari", "python-lzo", "xarray"],
    "dev": ["grpcio", "grpcio-tools", "napari", "python-lzo", "xarray"]
}

setup(
    name="napari-rpc",
    version="0.0.1",
    description="Use napari (https://github.com/napari/napari) remotely",
    long_description="",
    author="Burkhard Hoeckendorf",
    author_email="burkhard.hoeckendorf@pm.me",
    url="https://github.com/bhoeckendorf/napari-rpc",
    license="Apache License 2.0",
    packages=find_packages(exclude=("tests*", "docs*")),
    install_requires=_requirements["client"],
    extras_require=_requirements
)
