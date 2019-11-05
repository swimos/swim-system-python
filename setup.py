import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='swimai',
    version='0.1.0.dev1',
    author='Dobromir Marinov',
    author_email='dobromir@swim.it',
    description='Standalone Python framework for building massively real-time streaming WARP clients.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/swimos/swim-system-python',
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    keywords='swim client',
    install_requires=['websockets==8.0.2'],
)
