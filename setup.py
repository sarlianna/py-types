from setuptools import (
    setup,
    find_packages,
)
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md")) as rdme:
    with open(path.join(here, "CHANGELOG.md")) as chlog:
        readme = rdme.read()
        changes = chlog.read()
        long_description = readme + "\nCHANGELOG\n--------------------------------------\n" + changes


setup(
    name="py_types",
    version="0.1.0a",
    description="Gradual typing for python 3.",
    long_description=long_description,
    url="https://github.com/zekna/py-types",
    author="Zach Nelson",
    author_email="kzacharynelson@gmail.com",
    license="MIT",
    classifiers=[
        "Develpoment Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="type checking development schema",
    packages=find_packages(exclude=["tests*"]),

    install_requires=[],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
