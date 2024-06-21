from setuptools import setup, find_packages

setup(
    name="open_taxonomy",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "openai",
        "instructor"
    ],
    description="A library for working with taxonomy trees",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/Intuitive-Systems/open-taxonomy-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
