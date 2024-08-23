# pyright: basic

import setuptools

setuptools.setup(
    packages=setuptools.find_packages(
        where=".",
        include=["deferrer"],
        exclude=["__test__", "*_test"],
    ),
    package_data={
        "deferrer": ["py.typed"],
    },
)
