#!/usr/bin/env python3

from setuptools import setup

setup(name='linode-deploy-experimental',
      version='0.2',
      description='Deploy experimental disk images to Linode',
      author='Phil Eaton',
      url='https://github.com/eatonphil/linode-deploy-experimental',
      install_requires=['linode_api3'],
      packages=['linode_deploy_experimental'],
      entry_points={
          'console_scripts': ['linode_deploy_experimental = linode_deploy_experimental.__main__:main'],
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
    ],
)
