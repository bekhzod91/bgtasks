import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bgtasks",
    version="0.0.2",
    author="Bekhzod Tillakhanov",
    author_email="bekhzod.tillakhanov@gmail.com",
    description="Microservice with django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/myrubapa/bgtasks",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
