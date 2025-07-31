from setuptools import setup, find_packages

setup(
    name="PySVBench",
    author="SpaceProgrammer",
    version="0.6.2",
    packages=find_packages(),
    url="https://github.com/SpaceProgrammerOriginal/PySVBench",
    license="Custom",
    classifiers=[
        "License :: Other/Proprietary License"
    ],

    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown"
)