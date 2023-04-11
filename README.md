# INTI AI Learning Platform
Python Tkinter Desktop Application for Interactive Learning and Teaching with a focus on Collaboration and Communication. (Only Windows supported for now)

## Author
Matthew Loh Yet Marn

## Features
- Database hosted on Planetscale
- tbd
## Setup
- Dependencies (to be determined as well)
  - Python 3.11.3 (Developed On)
  - Prisma
  - mysql-connector-python
  - Pillow
  - pywin32
- Set `OPENAI_API_KEY` in your environment variables
  - [Get an API key here.](https://platform.openai.com/account/api-keys)
  - `import openai` automatically finds your key if you've set it to that name
- Create a virtual environment, in your terminal run the following command
```python -m venv venv```
- Create a .env file manually in the root directory of the project or in PowerShell run the following command:
``` New-Item -Path . -Name .env -ItemType File ```
- Add the following into the .env,
```
# Retrieved from Planetscale to connect through Prisma
DB_HOST=<DB_HOST>
DB_USERNAME=<DB_USERNAME>
DB_PASSWORD=<DB_PASSWORD>
DB_DATABASE=<DB_PASSWORD>
# Used for simple sql queries, obtained from Planetscale
DB_URL=<mysql_query>
```
## Usage
- Run `main.py` to start the application

## Project Directory
- TBD
