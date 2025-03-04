from setuptools import setup

setup(
    name="vcp1",
    version="0.0.1",
    author="John Doe",
    author_email="doe.john@example.com",
    description="vcp1 - A QtPyVCP based Virtual Control Panel for LinuxCNC",
    packages=["vcp1"],
    package_dir={"": "src"},
    install_requires=[
        "poetry-core",
        "versioneer[toml]"
    ],
    entry_points={
        'console_scripts': [
            'vcp1 = vcp1:main',
        ],
    },
)

