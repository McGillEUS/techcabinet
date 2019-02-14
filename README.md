# Tech Cabinet
Rental system for the EUS' tech cabinet! :package:

It is currently deployed here: https://rental.mcgilleus.ca/

The repository is split across two folders to separate its two major components.

# Front End
## Overview
The frontend is built in `React.js`, and most of it is found in these three files:
- `frontend/src/App.js`
- `frontend/src/components.js`
- `frontend/src/styles.js`

## Running it
To run the front-end, navigate to `frontend/` and run:
- `yarn install`
- `yarn start`

This should automatically run the page from localhost.

# Back End
## Overview
The backend is built using `Python` namely `Flask`. It has a `MySQL` database exposed via a `GraphQL` endpoint.

To learn more about the types of queries you can make to the backend, visit the [GraphQL documentation explorer](https://rental.mcgilleus.ca/graphql).

## Running it
To run the back-end, navigate to `backend/` and run:

- `python -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python setup.py`
- `python app.py`

Note that you need to have MySQL and Python3.6 installed; The use of f-strings will likely make the python scripts fail otherwise.

## Testing it
If you want to validate that your set-up is ready, you can go in the `backend/` folder and run:
```
pytest tests/
```
All 13 tests should pass!
