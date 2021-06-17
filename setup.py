from setuptools import setup

with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi-controller",
    version="0.0.8",
    author="Akshar Patel",
    author_email="akshar.patel.47@gmail.com",
    description="Package to create API controllers that can inherit routes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aksharpatel47/fastapi-controller",
    packages=["fastapi_controller"],
    install_requires=[
        "fastapi-utils>=0.2.1",
        "fastapi[all]>=0.65.0",
        "typing-inspect>=0.7.1"
    ],
    extra_require={
        'dev': [
            "pytest>=6.2.4",
            "pytest-asyncio>=0.15.1",
            "httpx>=0.18.1"
        ]
    },
    python_requires=">=3.6",
)
