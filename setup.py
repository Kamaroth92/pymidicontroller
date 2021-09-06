from setuptools import setup, find_packages

setup(
    name='pymidicontroller',
    version='0.1.0',    
    description='Easily map device and application controls to a midi controller',
    # url='https://github.com/shuds13/pyexample',
    author='Tane Barriball',
    author_email='tanebarriball@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests==2.26.0',
        'mido==1.2.10'
    ]
)
