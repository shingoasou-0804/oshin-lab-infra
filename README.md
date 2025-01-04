# oshin-lab-infra
- This is the repository where the Oshin team maintains its streamlit code.

## Required environment

- docker version 20.10.x or higher

## Setup and execution methods in Dev Container

```console
# Reopen in Container
<> → Dev Containers: Reopen in Container

# Python Version
$ poetry run python --version

# Add library
$ poetry add library_name

# Test
$ ./test.sh

# Boost
$ poetry run streamlit run home.py
```

## Local environment

Copy and paste the URL that appears in the log after executing “make up” into your browser.
- http://localhost:8501
