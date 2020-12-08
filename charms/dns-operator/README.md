# dns

## Description

Custom DNS server used for communication between IMS components

## Usage

DNS used for communication between IMS components. Fetches ip address through relations from pcscf, icscf,scscf and hss. Acts as custom dns server for the components within ims cluster to resolve the other components.


## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
