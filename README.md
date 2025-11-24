# March Madness Website
This repository contains the source code for a **March Madness Website**, a web application designed to run a March Madness bracket competition.

### Key Files
- **`main.py`**: The entry point of the application. Defines routes and handles user interactions.
- **`app/`**: Contains functions for interacting with the MySQL database.
    - **`auth/`**: flask routes for Login and Register pages
    - **`bracket/`**: flask routes for Bracket page
    - **`extensions/`**: db functions, constants and utils
    - **`static/`**: css, javascript code and images
    - **`templates/`**: html pages to render
    - **`app.py`**: creates the app, mounts blueprints e.t.c.
- **`sql_table_definitions/`**: SQL scripts for creating and managing the database schema.

### To Do
- Make separate page for analysis
- Make admin checks better by using LoginManager
- Add proper times to the games
- click on user name to see their bracket
- make bracket update to show current state of games
- Make the winner and the championship game text stand out