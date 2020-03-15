import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-beanstalk-worker",
    version="0.0.1",
    author="Gordon Wrigley",
    author_email="gordon.wrigley@gmail.com",
    description="A service for handling deferred and periodic tasks on beanstalk worker machines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tolomea/django-beanstalk-worker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["django-lazy-services", "boto3", "dateparser", "django"],
)
