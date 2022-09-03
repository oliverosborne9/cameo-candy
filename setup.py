from setuptools import find_packages, setup

NAME = "candy"
VERSION = "1.0.0"

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name=NAME,
    version=VERSION,
    description="Web server to draw and make RPi dispense",
    author="oliverosborne9",
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
)
