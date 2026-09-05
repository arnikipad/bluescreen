"""
BlueScreen Trigger v5.0 - Setup and Build Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="bluescreen-trigger",
    version="5.0.0",
    author="BlueScreen Dev Team",
    author_email="dev@bluescreen.local",
    description="Enterprise BSOD Generator with ML Analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arnikipad/bluescreen",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bluescreen=bluescreen_v5:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
