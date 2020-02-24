import os
from setuptools import setup

PACKAGE_NAME = "mmgphotos"

with open("README.md") as f:
    readme = f.read()

with open("VERSION") as f:
    version = f.read()

setup(
    # matadata
    name=PACKAGE_NAME,
    version=version,
    description="Magarimame's Google Photos Operation Library",
    long_description=readme,
    author="Yutaka Kato",
    author_email="kato.yutaka@gmail.com",
    url="https://github.com/yukkun007/mmgphotos",
    # liscence=
    # platform=
    # options
    packages=[PACKAGE_NAME],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=["google-api-python-client", "google-auth-oauthlib", "oauth2client"],
    entry_points="""
        [console_scripts]
        {app} = {app}.cli:main
    """.format(
        app=PACKAGE_NAME
    ),
)
