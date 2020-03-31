import os


def pytest_configure(config):
    os.environ['SNIPPETS_BUCKET'] = 'testbucket'
    os.environ['OUTPUT_DATA_BUCKET'] = 'outputbucket'
