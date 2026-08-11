Script created in conjunction with Gemini to create a query table from two separate tables in an Intersystems IRIS database.

Main script uses python libraries pandas and pyodbc.

Queries use Intersystems IRIS SQL parameter structures and syntax (or tries to).


FUTURE UPDATES:

  - pass in arguments to filters
  - include GUARANTOR_ID
  - wrap connection inside SQLAlchemy engine per pandas warning on CLI

GRAND SCHEME:

  - webapp to get query parameters from user, including client IDs as list,
  - run query inside docker container,
  - export formatted table to pdf template using html/css, creating a pdf for each client ID
