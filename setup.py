from setuptools import find_packages, setup


def readme():
    with open("README.md") as f:
        return f.read()


if __name__ == "__main__":
    setup(
        name="meru",
        description="",
        long_description=readme(),
        author="Roland von Ohlen",
        author_email="work@rvo.name",
        license="proprietary",
        url="",
        scripts=[],
        package_dir={"": "src"},
        packages=find_packages("src"),
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python",
        ],
        entry_points={},
        include_package_data=True,
        use_scm_version=True,
        extras_require={
            "develop": [
                "pytest==5.1.1",
                "pytest-asyncio==0.10.0",
                "pytest-cov==2.7.1",
                "pytest-freezegun==0.4.1",
                "pytest-mock==2.0.0",
                "git-pylint-commit-hook==2.5.1",
                "setuptools_scm==3.2.0",
            ]
        },
        install_requires=[
            "click==8.0.3",
            "pexpect==4.8.0",
            "pyzmq==22.3.0",
        ],
        zip_safe=True,
    )
