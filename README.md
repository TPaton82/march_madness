# March Madness Website
This repository contains the source code for a **March Madness Website**, a web application designed to run a March Madness bracket competition.

### Key Files
- **`main.py`**: The entry point of the application. Defines routes and handles user interactions.
- **`app/`**: Contains all code for the March Madness app
    - **`admin/`**: flask routes for Admin page
    - **`auth/`**: flask routes for Login and Register pages
    - **`bracket/`**: flask routes for Bracket page
    - **`extensions/`**: db functions, constants and utils
    - **`games/`**: flask routes for Games page
    - **`rules/`**: flask routes for Rules page
    - **`scoreboard/`**: flask routes for Scoreboard page
    - **`static/`**: css, javascript code and images
    - **`templates/`**: html pages to render
    - **`__init__.py`**: creates the app, mounts blueprints e.t.c.
- **`migrations/`**: Automatically generated scripts to handle any database migrations

### To Do
- fix seed script to have correct game ordering
- Make separate page for analysis
- Make admin checks better by using LoginManager
- Add proper times to the games
- click on user name to see their bracket
- make bracket update to show current state of games
- Make the winner and the championship game text stand out