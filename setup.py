from setuptools import setup

with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi-controller",
    version="0.0.5",
    author="Akshar Patel",
    author_email="akshar.patel.47@gmail.com",
    description="Package to create API controllers that can inherit routes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aksharpatel47/fastapi-controller",
    packages=["fastapi_controller"],
    install_requires=[
        "fastapi-utils>=0.2.1",
        "fastapi"
    ],
    python_requires=">=3.6",
)
