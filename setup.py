import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fault-tree-generator",
    version="0.0.1",
    author="Arjun Earthperson",
    author_email="mail@earthperson.org",
    description="Utility for creating synthetic fault trees",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/arjun372/fault-tree-generator',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'argparse',
        'ordered_set',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'fault-tree-generator=fault_tree_generator:main',
        ],
    },
)
