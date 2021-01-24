import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="recgov", 
    version="0.0.1",
    author="Carl Fischer",
    author_email="Carl.Fischer.IV@gmail.com",
    description="A package to find campsites at recreation.gov",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Carl4/recgov",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)