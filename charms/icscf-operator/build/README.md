# icscf

## Description

Interrogating CSCF is the entity that selects the appropriate SCSCF during registration

## Usage

This component works in selecting the appropriate SCSCF for the UE during its registration process with the IMS

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
