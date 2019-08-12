#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="EPFinder",
    version=0.0,
    author="caozixuan",
    author_email="1240292104@qq.com",
    description="An Efficient Plagiarism Code Detection Approach For Large Scale Student Assignments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas"
        ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
