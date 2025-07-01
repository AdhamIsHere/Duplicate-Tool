from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="duplicate_tool",
    version="0.2",
    packages=find_packages(),
    package_data={
        "Duplicate_Tool": ["resources/google-java-format-1.25.2-all-deps.jar"],
    },
    include_package_data=True,
    install_requires=[
        "torch",
        "transformers",
        "scikit-learn",
        "numpy"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "duplicate-tool=Duplicate_Tool.detection:main",
        ],
    },
    author="Adham Mohamed",
    description="A tool for detecting duplicate Java code using CodeT5 embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adham-mohamed/duplicate-tool",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
