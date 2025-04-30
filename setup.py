from setuptools import setup, find_packages

setup(
    name='internal-ticketing',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-migrate',
        'flask-wtf',
        'psycopg2-binary',
        'python-dotenv',
    ],
) 