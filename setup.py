from setuptools import setup, find_packages

setup(
    name='opengrok-search',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/shihxuancheng/opengrok-search',
    license='MIT',
    author='Richard Shih',
    author_email='richard_shih@wanhai.com',
    description='Opengrok Search CLI',
    install_requires=[
        'pandas==2.2.3',
        'requests==2.32.3',
        'openpyxl==3.1.5',
        'tqdm==4.67.1'
    ],
    entry_points={
        'console_scripts': [
            'opengrok-search=opengrok_util.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)