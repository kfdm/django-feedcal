from setuptools import find_packages, setup
from feedcal import __version__

setup(
    name='django-feedcal',
    version=__version__,
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    license='MIT License',
    description='A simple feed/icalendar mangler',
    url='https://github.com/kfdm/django-feedcal',
    author='Paul Traylor',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'icalendar',
        'requests',
    ],
    entry_points={
        'powerplug.apps': ['feedcal = feedcal'],
        'powerplug.urls': ['feedcal = feedcal.urls'],
        #'powerplug.rest': ['location = position.views:LocationViewSet'],
    },
)
