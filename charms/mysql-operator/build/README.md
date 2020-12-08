# mysql

## Description

Database for storing user profile and location data.

## Usage

Database for storing user profile and location data. All components in IMS connects with mysql to store and retrieve necessary details.


## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
