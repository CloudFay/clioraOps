from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clioraops",  
    version="0.1.0",
    author="Faith Omobude",
    author_email="fayosarumwense@gmail.com",
    description="DevOps learning and architecture companion CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CloudFay/clioraOps",

    # Only include your package
    packages=find_packages(include=["clioraOps_cli", "clioraOps_cli.*"]),

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],

    python_requires=">=3.9",

    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "prompt-toolkit>=3.0.0",
    ],

    # Optional heavy dependencies
    extras_require={
        "visualizer": [
            "diagrams>=0.23.0",
            "graphviz>=0.20.0",
        ]
    },

    entry_points={
        "console_scripts": [
            # ✅ Updated to your Click entry point
            "clioraops=clioraOps_cli.main:main",
        ],
    },

    include_package_data=True,
    zip_safe=False,
)
