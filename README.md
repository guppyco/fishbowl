# fishbowl

A cash back search engine.

## Principles:

1. Everyone can participate.
1. All of these principles are subject to change:
   > [The voyage of the best ship is a zigzag line of a hundred tacks. See the line from a sufficient distance, and it straightens itself to the average tendency.](https://www.gutenberg.org/files/16643/16643-h/16643-h.htm#Page_91)

## Tech principles:

1. No third-party javascript.
1. The site can be run without javascript.
1. Code should be simple enough for anyone to participate.
1. All code is open source.
1. Adhere to the [code of conduct](./CODE-OF-CONDUCT.md).

## Search algorithm:

TK

## Data sources
We pulled [Alexa's top million websites](http://s3.amazonaws.com/alexa-static/top-1m.csv.zip), found via [Quora](https://www.quora.com/What-are-the-top-100-000-most-visited-websites) to determine the top sites on the internet to start searching first.

## Deployments:

1. Install Ansible
2. Pull `ian` branch from https://github.com/YPCrumble/deployments
3. For new server only (first deployment):
- Run secure scripts: `. bin/guppy_<environment>/secure-guppy-<environment>.sh`
- Run setup scripts: `. bin/guppy_<environment>/setup-guppy-<environment>.sh`
4. Run deployment scripts: `. bin/guppy_<environment>/deploy-guppy-<environment>.sh`

## Setting up the Python development server

1. Create your virtualenvironment
1. Setup PostgreSQL, create user, database
1. Create `.env` in the root of the project directory base on `.env.example` and provide the configs (DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, ...)
1. Install wheel with `pip install wheel`
1. Install dependencies into your virtualenvironment with `pip install -r requirements/local.txt`
1. Install frontend dependences via yarn (or npm): `cd ./frontend && yarn` or `cd ./frontend && npm install`
1. Run migrations with `python manage.py migrate`
1. Create super user with `python manage.py createsuperuser`
1. Start the server with `python manage.py runserver`

*Tip:* If you get the error when installing dependencies, try to install the pakages: libssl-dev, libffi-dev, libpq-dev, gcc, libmemcached-dev
