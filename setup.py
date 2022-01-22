from os import path
import setuptools
import hydralit as hy

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name=hy.__packagename__,
    version=hy.__version__,
    description='Multi-app Streamlit library.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tanglespace/hydralit',
    author=hy.__author__,
    author_email='c6lculus8ntr0py@gmail.com',
    license="Apache 2",
    project_urls={
        'Documentation': 'https://github.com/tanglespace/hydralit',
        'Source': 'https://github.com/tanglespace/hydralit',
        'Tracker': 'https://github.com/tanglespace/hydralit/issues',
    },
    packages=setuptools.find_packages(),
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        'streamlit >=1.3.1',
        'compress_pickle',
        'hydralit_components>=1.0.7',
        'validators',
        'pyjwt',
        'bokeh',
    ],
    python_requires='>=3.6',
    keywords=[
        'Streamlit',
        'Web',
        'Machine Learning',
        'Deployment',
        'Web Application',
        'Analysis',
        'Data Modelling',
        'Presentation',
    ],
)
