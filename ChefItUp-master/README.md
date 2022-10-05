# ChefItUp

A fully functional cooking assistance platform made as part of our COM2022 Software Engineering final summative assessement.

## Setup
### Requirements
- Any Linux Distribution (Windows OS is not compatible)
- Python Version: 3.6.9

### Guide
1) Ensure you have all the Prerequisites packages (pip, python, virtualenv) installed.

2) Create an Empty Folder and Clone This Repository Inside.

```git clone https://github.com/Satilianius/ChefItUp.git```

3) Navigate inside the folder and create a Virtual Environment folder.

```virtualenv [virtual environment folder name]```

4) Run the activate script from the environment folder to activate the virtual environment.

```
cd [virtual environment folder name]/bin
source activate
```

5) Install all the necessary project libraries inside the Virtual Environment Folder.

```pip install -r ../../requirements.txt```

*The following point was added only for convinience of the sponsors while checking our solution. The actual API keys would never be under version control in a real world project

6) Add to system path the environment variables, by adding the following lines to ~/.bashrc file:
```
export ENV_TYPE=development
export SECRET_KEY='_p07e+w8=vy)x9mn*=84g4m&l98+@387pxvk^v(8of$3^_a7sw'
export DEBUG=True
export SPOONACULAR_API_KEY='6970141a8e614bed85d4bbf75ca39f08'
export SENDGRID_API_KEY='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'
```
In the same way add the variable with the path to the file where you want to store the sqlite database:
```
export DATABASE_URL='sqlite:////home/username/PycharmProjects/ChefItUp/db.sqlite3'
```
Reload the ~/.bashrc file by executing 
```source ~/.bashrc```

7) Navigate back to main directory and run migrations

```python manage.py migrate```

8) Load fixtures

```python manage.py loaddata simple_recommendations```
```python manage.py loaddata collab_fixture.json```

## Running the Server
- **Launch the server on the default Django Port.**
```python manage.py runserver```

- **Launch the server on a specific port.**
```python manage.py runserver 127.0.0.1:8000```
