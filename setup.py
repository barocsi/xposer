from setuptools import find_packages, setup


def read_requirements():
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    return requirements


setup(
    name='xposer',
    version='0.9.15',
    packages=find_packages(),
    install_requires=read_requirements(),
    author='Aron Barocsi',
    author_email='aron.barocsi@gmail.com',
    description='Xpose your functions as microservices over arbitrary channels using standardized logging and configuration',
    license='Private',
    keywords='Expose functions wrapperd',
    url='URL to the package repository',
    )
