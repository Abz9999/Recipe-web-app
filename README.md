# Team Scarlet-4 Small Group project

## Team members
The members of the team are:
- Aishah Ahmed
- Abdallah Batah
- Aishah Imran
- Katie Nguyen
- Adam Zakieh

## Attribution
This project was completed as part of a university group coursework.
This repository is a personal mirror created for portfolio and demonstration purposes.


## My Contributions
- Extended and integrated existing authentication templates to implement login and sign-up flows, including form handling and validation
- Designed and built tag functionality to support content categorisation and filtering
- Developed search functionality on the welcome page to enable efficient querying and content discovery
- Contributed to front-end implementation using Bootstrap, improving layout consistency and usability
- Contributed to writing and maintaining automated tests to verify core functionality and prevent regressions


## Project structure
The project is called `recipify`.  It currently consists of a single app `recipes`.

## Deployed version of the application
The deployed version of the application can be found at https://adamzakieh.pythonanywhere.com.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  The project source code has been developed using Python 3.12, so you are recommended to use the same version.  From the root of the project:

```
$ python3.12 -m venv venv
$ source venv/bin/activate
```

If your system does not have `python3.12` installed and you are unable to install Python 3.12 as a version you can explicitly refer to from the CLI, then replace `python3.12` by `python3` or `python`, provide this employs a relatively recent version of Python.

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```


## Sources
The packages used by this application are specified in `requirements.txt`

AI was used for for generating foods in the seed.py, as well as debugging CSS.

We approximate less than 30% of the two mentioned files contents are AI-generated.
