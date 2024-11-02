from setuptools import setup, find_packages

setup(
    name='django_i18nutils',
    version='0.1.0b1',
    description='A Django package for handling internationalized fields.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Maurizio Melani',
    author_email='maurizio@forwalk.org',
    url='https://github.com/forwalk-org/django_i18nutils',  
    packages=find_packages(exclude=('tests',)), 
    package_dir={"i18nutils": "i18nutils"},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=3.2',  
    ],
    python_requires='>=3.6', 
)
