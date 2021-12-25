import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(here, "README.md")).read()

setuptools.setup(
    name="mrsd",
    version="0.1.0",
    
    description="MR sequence diagram toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    url="https://github.com/lamyj/mrsd",
    
    author="Julien Lamy",
    author_email="lamy@unistra.fr",
    
    license="MIT",
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Matplotlib",
        "Intended Audience :: Education",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    
    keywords = ["MRI", "sequence", "diagram", "matplotlib"],
    
    packages=["mrsd"],
    package_dir={"mrsd": "src/mrsd"},
    
    python_requires=">=3.5",
)
