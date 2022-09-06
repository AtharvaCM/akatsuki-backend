# akatsuki-backend

## Project setup

### 1. Create a virtual environment in your project directory called _env_

Open a shell and run the following command

```bash
python -m venv venv
```

This will create a virtual environment called 'venv' in your project directory

### 2. Create a `.env` file and add the following environment variables

- SECRET_KEY

### 3. Create a `.flaskenv` file and add the following environment variables

- FLASK_DEBUG
- FLASK_APP
- SQLALCHEMY_DATABASE_URI

## Start the application server

In the root of your project directory, run the following command

```bash
flask run
```

## Inserting Records in DB

### Run flask shell

```bash
python -m flask shell
```

Import the _db_ istance in shell environment

```shell
from src.database import db
```

Import Model in shell environment

```shell
from src.models.<ModelName> import <Model>
```

Add records

```shell
record=ModelConstructor(id=1, ...)
```

Add the records to the session and then commit the session

```shell
db.session.add(record)
db.session.commit()
```
