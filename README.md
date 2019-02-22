# hub
Microservices point with providing authentication and data, integrated as an API Gateway.

switch-hub provides services for Vidyut websites and mobile apps. Check the API documentation at /doc. By default, the development server runs on port 3000.

## Installation

Clone the repo into the directory of your choice. Please make sure you have Python 3 installed.
~~~
git clone https://github.com/nandujkishor/hub.git
~~~
Please create a virtual environment in Python 3 to manage dependencies and their versions, and for proper isolation. The following command, on execution, creates a virtual environment with name *venv*
~~~
python3 -m venv venv
~~~
Enter the virtual environment
~~~
. venv/bin/activate
~~~
Then install the requirements
~~~
pip install -r requirements.txt
~~~

Please make the environment variable FLASK_APP set to the file *hub.py*

In Linux or UNIX devices, this can be done via
~~~
export FLASK_APP=hub.py
~~~

## To run the app

Be inside the switch directory.
~~~
flask run
~~~

To enable debugging during development, set FLASK_ENV environment variable to "development" (without the quotes).

~~~
export FLASK_ENV=development
export FLASK_DEBUG=true
~~~
