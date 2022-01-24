# Borneo Technical Assessment

This application is built to search documents from Dropbox based on the content inside the document.
[Tornado](http://tornadoweb.org/) Web Framework is used with Python for the backend.

## Requirements before deploying this project

### Python version

This application requires Python version v3.8.10 and above.

### Elasticsearch

This application requires Elasticsearch to be install on the machine. (https://www.elastic.co/downloads/elasticsearch)

Development work was done on Ubuntu 20.04 and this [guide](https://www.elastic.co/guide/en/elasticsearch/reference/7.16/deb.html#deb-repo) was followed to install Elasticsearch for my machine.

### Install pip

pip is a handy tool to install libraries/dependencies for your python programs. pip should already come installed on your system. Head over to https://pip.pypa.io/en/stable/installing/ for steps to install pip if it's not available.

### Install virtualenv

We use virtualenv to create an isolated running environment to install dependencies and launch the web application. Head over to https://virtualenv.pypa.io/en/latest/installation.html for instructions to install virtualenv.

### Install dependencies

Once you have pip and virtualenv set up, we can proceed to create the environment to run our web applications:

```bash
# Locate the path for the Python 3 installation
which python3

# Create the virtual environment in a folder named "env" in the current directory
virtualenv env --python=<path_to_python_3>

# Start the virtual environment
source env/bin/activate

# Install the required dependencies/libraries
pip install -r requirements.txt
```

You'll see `(env)` show up at the beginning of the command line if you've started virtual environment successfully.
To check if the dependencies are installed correctly, run `pip freeze` and check if the output looks something like this:

```
tornado==6.1
```

## Deployment

1. Create a .env file in the main folder and key in the Dropbox Access Token:

```
DROPBOX_ACCESS_TOKEN=<YOUR_DROPBOX_ACCESS_TOKEN>
```

2. Navigate to the main folder and run the service:

```
# Run the server
python server.py
```

## Troubleshooting

I ran into a problem that Elasticsearch was unable to start in my machine due to insufficient memory issue.
And this [solution](https://stackoverflow.com/questions/58656747/elasticsearch-job-for-elasticsearch-service-failed) from Stackoverflow was able to solve the issue for me.

```
Open /etc/elasticsearch/jvm.options in your nano editor using the command below:

sudo nano /etc/elasticsearch/jvm.options
First, un-comment the value of Xmx and Xms

Next, modify the value of -Xms and -Xmx to no more than 50% of your physical RAM.
The value for these settings depends on the amount of RAM available on your server
and Elasticsearch requires memory for purposes other than the JVM heap
and it is important to leave space for this.
```
