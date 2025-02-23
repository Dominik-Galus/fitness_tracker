# Fitness Tracker
As the name suggests, the app traces workouts, whether at the gym or at home (calorie counting will be added in the future).
## Database
![Untitled-2](https://github.com/user-attachments/assets/819e5af1-8409-422b-93c5-e9a5725c5864)
On the database side, fastapi was used, in which the application on the site calls the appropriate endpoints to get the data.
On the database side, it was assumed that the user would only add exercises that already exist in the database.

In the database we have check constraints for:
On set table:
- weight $\ge$ 0
- repetitions > 0
  
On profile table:
- age > 0
- weight > 0
- height > 0

Downloading using pip:
```
python3 -m pip install .
```
There is a built-in cli that populates the exercise tables by calling the WGER API. But before that you need to migrate the database either by executing api:
```
start-api --host 127.0.0.1 --port 8000
```
or:
```
python3 -m fitness_tracker.main
```
Then we will initialize the database and to populate the exercise tables we can:
```
fill-exercises
```
Of course, you can fill the exercise tables yourself, using your scripts etc.
And the only thing left is to run the program:
```
start-api --host 127.0.0.1 --port 8000
```
The basic values for host are: 127.0.0.1 and for port: 8000.

## Frontend side
Jako frontend został użyty Vue.js:
```
npm run build
```
