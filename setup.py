from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='rootrouter',
    version='0.1.0',
    description='IoT plant moisture monitoring system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Amin Alam',
    author_email='ma.alamalhoda@gmail.com',
    url='https://github.com/AminAlam/RootRouter',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'rootrouter=server.src.main:run',
        ],
    },
) 