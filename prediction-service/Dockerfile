# TODO: Create own alpine image
FROM pypy:3

# Set the working directory to /app
WORKDIR /app/src

# Copy the current directory contents into the container at /app
ADD src /app/src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 755 /app/src/main.py

CMD ["pypy3", "-u", "main.py"]
