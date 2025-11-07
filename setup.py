from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="graz-library-bulk-ops",
    version="0.1.0",
    author="Martin Jost",
    author_email="git@mjost.at",
    description="Bulk operations tool for Stadtbibliothek Graz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/graz-library-bulk-ops",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "playwright>=1.40.0",
        "click>=8.1.0",
        "python-dateutil>=2.8.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "isort>=5.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "graz-library=graz_library.cli:main",
        ],
    },
)
