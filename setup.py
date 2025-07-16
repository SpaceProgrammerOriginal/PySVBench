from setuptools import setup, find_packages

setup(
    name="PySVBench",
    version="0.1.1",
    packages=find_packages(),

    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown"
)