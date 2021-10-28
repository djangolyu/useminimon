# Editable mode currently requires a setup.py based build.
import setuptools

setuptools.setup(
        name="use-minimon-dj",
        version="0.1.0",
        author="Djang Lyu",
        description="To make use of Renesas' MiniMonitor",
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        python_requires=">=3.6",
)
