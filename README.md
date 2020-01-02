# FlightFinder

FlightFinder is a flask app that provides users register, log in, search, book and manage booked flights easily.

## Requirements

- Have at least Python 3.7.x installed.
  - NOTE: if installing on windows, tick `Add Python to PATH`
- Have MySQL and phpMyAdmin installed.
  - For Windows/Linux: install [XAMPP](https://www.apachefriends.org/download.html)
  - For MacOS: install [MAMP](https://downloads.mamp.info/MAMP-PRO/releases/5.5/MAMP_MAMP_PRO_5.5.pkg)

## Project Setup

- Clone the repo or download as zip.
- Navigate to the folder where you cloned/extracted the repo.
- Run `python generate_dotenv.py` to generate .env file.
- Create a virtual environment using `python -m venv venv` command.
- Activate virtual environment.
  - On Windows: `venv\bin\activate.bat`
  - On MacOS/Linux: `source venv/bin/activate`
- Run `pip install -r requirements.txt` to install dependencies.
- Navigate to `/app/utilities` and run `python generate_db.py` to create and initialize database.

## Running App

- Run `python app.py`
- Navigate to `http://127.0.0.1:5000` and you are done.

## Technologies Used

- [Flask](https://www.palletsprojects.com/p/flask/) - Python web framework used
- [MySQL](https://www.mysql.com/) - Relational database management system used.
- [WAMP/MAMP/LAMP Bundle](https://www.oreilly.com/library/view/learning-php-mysql/9781449337452/ch02s01.html) - Apache, MySQL, PHP softwares used.

## Authors

- Neoptolemos Kyriakou
- Aggelos Pournaras

## Credits

- [Daemonite](https://daemonite.github.io/material/) for the material boostrap frontend framework.
- [Fezvrasta](https://github.com/FezVrasta/snackbarjs/) for the snackbar functionality.
- [Mateuszmarkowski](https://github.com/mateuszmarkowski/jQuery-Seat-Charts/) for the seat map functionality.
- [Djibe](https://github.com/djibe/Bootstrap-4-Advanced-Components) for the extra functionality of some of the components of material.
- [Rajendra](https://www.behance.net/gallery/1041969/FlightFinder-Logo-Design) for the logo icon.

## LICENSE

- This project is licensed under the MIT License - see the [LICENSE](https://github.com/STiXzoOR/up-flightfinder/blob/master/LICENSE) file for details.
