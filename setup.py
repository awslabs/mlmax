import os

from setuptools import find_packages, setup

_pkg: str = "mlmax"
_version: str = "0.1.0"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Declare minimal set for installation
required_packages = []

setup(
    name=_pkg,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    version=_version,
    description="This package does x,y,z.",
    long_description=read("README.md"),
    author="Firstname Lastname",
    author_email="first.last@email.com",
    url=f"https://github.com/abcd/{_pkg}/",
    download_url="",
    project_urls={
        "Bug Tracker": f"https://github.com/abcd/{_pkg}/issues/",
        "Documentation": f"https://{_pkg}.readthedocs.io/en/stable/",
        "Source Code": f"https://github.com/abcd/{_pkg}/",
    },
    license="MIT",
    keywords="word1 word2 word3",
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
