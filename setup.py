from setuptools import setup, find_packages

setup(
    name="django_i18nutils",
    version="2.0.0",
    description="Lightweight Django internationalized model fields backed by JSONField.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Maurizio Melani",
    author_email="maurizio@forwalk.org",
    url="https://github.com/forwalk-org/django_i18nutils",
    packages=find_packages(exclude=("tests", "test_project")),
    package_dir={"i18nutils": "i18nutils"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Internationalization",
    ],
    install_requires=[
        "Django>=3.2",
    ],
    python_requires=">=3.8",
)
