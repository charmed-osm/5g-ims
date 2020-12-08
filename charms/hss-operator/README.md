# hss

## Description

Home Subscriber Subsystem  maintains user profile and location details.

## Usage

HSS is the application used to maintain the user profile and authentication details. Other components in IMS connects with HSS if authentication details needs to be verified.


## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
