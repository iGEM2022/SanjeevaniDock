from setuptools import setup, find_packages

setup(
    name             = "sanjeevani_dock",
    version          = "1.0.0",
    author           = "IISER Thiruvananthapuram iGEM'26 Dry Lab",
    description      = (
        "Automated bare heavy-metal ion docking to metallothioneins "
        "using AutoDock 4.2.6"
    ),
    long_description              = open("README.md", encoding="utf-8").read(),
    long_description_content_type = "text/markdown",
    url              = "https://github.com/iGEM2022/SanjeevaniDock",
    license          = "MIT",
    packages         = find_packages(),

    py_modules       = ["run_dock"],
    python_requires  = ">=3.8",
    install_requires = [],
    entry_points     = {
        "console_scripts": [
            "sanjeevani-dock = run_dock:main",
        ],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Intended Audience :: Science/Research",
    ],
)
