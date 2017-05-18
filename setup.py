from setuptools import setup, find_packages


requirements = [
    'py3dtiles',
    'psycopg2',
]


setup(
    name='pgpc2tile',
    version='0.0.1',
    description='Export PostgreSQL point clouds as 3D Tiles sets',
    url='https://github.com/elemoine/pgpc2tile',
    author_email='eric.lemoine@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    include_package_data=True,
    test_suite='tests',
    install_requires=requirements,
    entry_points={
        'console_scripts': ['pgpc2tile = pgpc2tile.main:main'],
    }
)
