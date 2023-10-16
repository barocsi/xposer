from setuptools import find_packages, setup


def read_requirements():
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    return requirements


setup(
    name='xposer',
    version='0.9.13',
    packages=find_packages(),
    install_requires=read_requirements(),
    author='Aron Barocsi',
    author_email='aron.barocsi@gmail.com',
    description='Xpose arbitrary functions over arbitrary channels using standardized logging and configurations',
    license='Private',
    keywords='Expose functions wrapperd',
    url='URL to the package repository',
    )
