from setuptools import setup, find_packages

import webnovel

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name='webnovelbot',
    version=webnovel.__version__,
    author="Schicksal",
    description="webnovel scraper using selenium",
    author_email='mhaisham79@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=requirements,

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        "Operating System :: OS Independent",
    ],
    license="MIT license",
    keywords='webnovel novel bot api',

    url='https://github.com/mHaisham/webnovelbot',
    project_urls={
        'Source code': 'https://github.com/mHaisham/webnovelbot'
    },
    packages=find_packages(),
    python_requires='>=3.6'
)
