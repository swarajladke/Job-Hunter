from setuptools import setup, find_packages

setup(
    name="h1b-job-hunter",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "openpyxl",
        "beautifulsoup4",
        "playwright"
    ],
    entry_points={
        "console_scripts": [
            "h1b-job-hunter=h1b_job_hunter.cli:main"
        ]
    }
)

