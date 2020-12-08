# pcscf

## Description

pcscf-operator charm does the function of proxy-cscf for IMS

## Usage

pcscf-operator charm does the function of proxy-cscf for IMS. This stands as the entry and exit to any request to IMS

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
