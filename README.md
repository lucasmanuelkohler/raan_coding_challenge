# RAAN coding challenge
Flask app for the coding challenge. 

## Data
Data must be given as .xlsx file with the specific format for the task. 
When the app is run, the file can be uploaded to the app. 
After successfully uploading the data, a 2d and a 3d plot of the network opens. 


## How to run the app:<br />
To run the app download the repository:

Open a terminal window and set the current directory to the desired folder: <br />
`cd ...`

Clone the git repository (install git first) or download directly from [GitHub](https://github.com/lucasmanuelkohler/raan_coding_challenge.git): <br />
`git clone https://github.com/lucasmanuelkohler/raan_coding_challenge.git`

Go to this folder: <br />
`cd raan_coding_challenge`

Optionally set new python environment: <br />
`python3 -m venv venv` <br />
`source venv/bin/activate
`

Install the requirements: <br />
`pip install -r requirements.txt`

Run the app: <br />
`python app.py`

Open the displayed URL in a web browser and upload the given file [Flask App](http://127.0.0.1:5000/).

If a new environment was create, deactivate it with: <br />
`deactivate` or `source deactivate` 

Heroku app:<br />
Additionally, I deployed the app on the Heroku hosting service.
The app can be open there using the following link [Heroku App](https://raan-app.herokuapp.com)
