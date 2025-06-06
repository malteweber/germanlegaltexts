# Tests for germanlegaltexts

This directory contains tests for the germanlegaltexts package.

## Running the tests

You can run the tests directly using pytest:

```bash
python -m pytest
```

## Test structure

The tests are organized as follows:

- `conftest.py`: Contains pytest fixtures for loading XML files
- `test_gesetzbuch.py`: Tests for the `Gesetzbuch` class
- `test_downloader.py`: Tests for the `GermanLegalTextDownloader` class

## Test coverage

The tests cover the following functionality:

### Gesetzbuch
- Parsing XML content into a `Gesetzbuch` instance
- Retrieving all paragraphs from a `Gesetzbuch` instance
- Retrieving all sections from a `Gesetzbuch` instance
- Retrieving a specific paragraph from a `Gesetzbuch` instance
- Retrieving a specific section from a `Gesetzbuch` instance
- Parsing multiple XML files into `Gesetzbuch` instances

### GermanLegalTextDownloader
- Verifying the base URL of the downloader
- Testing URL formation for downloading laws

## Adding new tests

To add new tests, create a new test file in this directory with a name starting with `test_`. The test file should contain test functions with names starting with `test_`.

For example, to add tests for a new class `MyClass`, create a file `test_myclass.py` with test functions like `test_my_method()`.
