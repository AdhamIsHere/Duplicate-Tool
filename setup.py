from setuptools import setup, find_packages

setup(
    name="Duplicate_Tool",
    version="0.1",
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

    author="Adham Mohamed",
    description="A tool for detecting duplicate Java code",
)
