from setuptools import setup

setup(
    name='revision-recorder', # the name of the package
    version='1.0',
    packages=['package'], # contains our actual code
    author='ben',
    author_email='ben@merovex.com',
    description='Capture todos in Markdown as GH Issues',
    scripts=['bin/capture-revisions.py'], # the launcher script
    install_requires=[
        "pyyaml",
        "PyGithub"
    ] # our external dependencies
)

