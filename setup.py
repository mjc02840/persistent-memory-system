#!/usr/bin/env python3
"""
Setup script for Persistent Memory System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="persistent-memory-system",
    version="1.0.0",
    author="Persistent Memory Contributors",
    description="A unified system for capturing, searching, and enriching responses with historical context",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/persistent-memory-system",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[],  # No external dependencies!
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "persistent-memory=action_logger:main",
        ]
    },
)
