
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='simple-api-mock-server',
    version='0.3.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'jsonschema',
        'watchdog',
        'Flask-Cors',
        'PyYAML'
    ],
    extras_require={
        'dev': ['requests', 'pytest'] # pytest is also a dev dependency
    },
    entry_points={
        'console_scripts': [
            'simple-mock-server=simple_mock_server.server:main',
        ],
    },
    author='Sanat Ladkat',
    author_email='arsanatladkat@gmail.com',
    description='A simple, file-based API mocking server.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sanatladkat/simple-api-mock-server',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Topic :: Software Development :: Testing',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    ],
    python_requires='>=3.7',
)
