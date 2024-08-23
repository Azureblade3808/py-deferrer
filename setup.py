# pyright: basic

import setuptools

setuptools.setup(
    packages=["deferrer"],
    package_data={
        "deferrer": ["py.typed"],
    },
)
