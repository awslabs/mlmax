import os
from typing import List

from setuptools import find_packages, setup

_pkg: str = "mlmax"
_version: str = "0.2.0"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Declare minimal set for installation
required_packages: List[str] = []

setup(
    name=_pkg,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    version=_version,
    description="This package provides a template for ML Inference and Training",
    long_description=read("README.md"),
    author="Amazon Web Services",
    url=f"https://github.com/awslabs/{_pkg}/",
    project_urls={
        "Bug Tracker": f"https://github.com/awslabs/{_pkg}/issues/",
        "Documentation": f"https://{_pkg}.readthedocs.io/en/stable/",
        "Source Code": f"https://github.com/awslabs/{_pkg}/",
    },
    license="Apache License 2.0",
    keywords="ML Amazon AWS AI template",
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6.0",
    install_requires=required_packages,
)
