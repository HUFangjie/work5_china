from setuptools import find_packages, setup

setup(
    name="qticket",
    version="0.1.0",
    description="Pluggable evaluation framework for rail-ground communication authentication and rebinding",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
