# savvy business-model-optimization

from setuptools import setup, find_packages

setup(
    version="0.1.0",
    name='business-model-optimization',
    description="business model optimization",
    packages=["savvy"],
    scripts=["scripts/sim.py"],
    include_package_data=True,
    keywords='',
    author="idm",
    author_email="",
    install_requires=[
        "pytest",
        "click",
        "trogon",
        "rich",
        "watchdog[watchmedo]",
        "hiplot",
        "pandas",
        "jupyterlab",
        "scipy",
        "matplotlib",
    ],
    license='proprietary',
    zip_safe=False,
)
