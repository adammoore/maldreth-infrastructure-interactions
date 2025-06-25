"""
setup.py

Setup configuration for the MaLDReTH Infrastructure Interactions package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="maldreth-infrastructure",
    version="1.0.0",
    author="MaLDReTH Development Team",
    author_email="support@maldreth.org",
    description="Interactive visualization and management system for the research data lifecycle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/maldreth-infrastructure",
    packages=find_packages(exclude=["tests", "tests.*", "backup_*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-flask>=1.2.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "pre-commit>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "maldreth-init=scripts.init_maldreth_tools:main",
            "maldreth-migrate=scripts.migrate_maldreth_data_standalone:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*", "static/*", "data/*"],
    },
)
