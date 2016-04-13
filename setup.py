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
    install_requires=['pygerduty==0.32.1',
                      'PyYAML==3.11',
                      'slacker==0.9.0'],
    entry_points={
        'console_scripts': [
            'slack-duty = slack_duty:main'
        ]
    }
)
