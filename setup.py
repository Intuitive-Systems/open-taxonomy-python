from setuptools import setup, find_packages

setup(
    name="open_taxonomy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai",
    ],
    description="A library for working with taxonomy trees",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/my_taxonomy_lib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
