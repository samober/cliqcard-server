from setuptools import setup

setup(
    name='cliqcard-server',
    packages=['cliqcard_server'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'psycopg2-binary',
        'flask-migrate',
        'pyjwt',
        'flask-bcrypt',
        'phonenumbers',
        'twilio'
    ],
)