from setuptools import setup

setup(
    name='slack-duty',
    version='0.1.0',
    py_modules=['slack_duty'],
    url='https://github.com/backstop/slack-duty',
    license='',
    author='Backstop Solutions',
    author_email='',
    description='',
    entry_points={
        'console_scripts': [
            'slack-duty = slack_duty:main'
        ]
    }
)
