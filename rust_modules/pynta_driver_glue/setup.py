from setuptools import setup
from setuptools_rust import RustExtension


setup(
    name="pynta_drivers",
    version="0.1.0",
    classifiers=[
        "License :: GPL3",
        # "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Rust",
        "Operating System :: Windows",
        "Operating System :: Linux",
    ],
    packages=["pynta_drivers"],
    rust_extensions=[
        RustExtension(
            "pynta_drivers._pynta_drivers",
            debug=False,
        ),
    ],
    include_package_data=True,
    zip_safe=False,
)