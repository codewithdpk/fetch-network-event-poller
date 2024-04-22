import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='eventfetcher',
    version='1.0.0',
    author='Chirag Maliwal', 
    author_email='chirag.maliwal@fetch.ai',
    description='A utility for fetching events from fetch network',
    long_description = read("README.md"),
    long_description_content_type="text/markdown",
    packages=['eventfetcher'],
    install_requires=['certifi', 'grpcio', 'cosmpy'],  # Add any required dependencies
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)