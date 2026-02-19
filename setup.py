from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clioraops",  
    version="0.3.0",
    author="Faith Omobude",
    author_email="fayosarumwense@gmail.com",
    description="Your Intelligent DevOps Mentor powered by Multi-Provider AI",
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
        "rich>=10.0.0",
        "pyyaml>=6.0",
        "prompt-toolkit>=3.0.0",
        "requests>=2.28.0",
        "google-generativeai>=0.3.0",
        "diagrams>=0.23.0",
        "graphviz>=0.20.0",
        "gradio>=4.0.0",
        "python-dotenv>=1.0.0",
    ],

    entry_points={
        "console_scripts": [
            # ✅ Updated to your Click entry point
            "clioraops=clioraOps_cli.main:main",
        ],
    },

    include_package_data=True,
    zip_safe=False,
)
