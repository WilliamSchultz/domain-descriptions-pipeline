# Dockerfile that builds a container and runs the main.py script in the repo
FROM python:3.10.9

# Install pip
RUN python -m pip install --upgrade pip

# Install dependencies from requirements.txt
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt && pip install psycopg2 && pip install telebot

# Copying everything from project directory to our container
COPY . /app/
WORKDIR /app

# Run the main.py script
CMD ["python", "main.py"]

