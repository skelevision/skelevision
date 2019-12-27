import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

URL = "https://github.com/RCoanda/skelevision"

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
]

setuptools.setup(
    name="skelevision",
    version="0.1.4",
    description="Log Skeleton Visualizer and Browser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    python_requires='>=3.7',
)
