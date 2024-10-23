import os
from setuptools import setup, find_packages


LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

VERSION = os.environ.get("GITHUB_REF", "v0.1.0").lstrip("refs/tags/").lstrip("v")

setup(
    name="fields-of-gold",
    version=VERSION,
    packages=find_packages(),
    description="A Django library for providing useful DB model fields.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Adam Alton",
    author_email="270255+adamalton@users.noreply.github.com",
    url="https://github.com/adamalton/fields-of-gold",
    keywords=["Django", "Pydantic", "JSON", "JSONField", "Schema"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        'django>=4.2,<6.0',
        'pydantic>2.0,<3.0',
    ],
    include_package_data=True,
    # extras_require={
    #     'test': [
    #     ]
    # },
)
