# TODO: Create own alpine image
FROM pypy:3

# Get Rust; NOTE: using sh for better compatibility with other base images
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Add .cargo/bin to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Add GA Library
WORKDIR /app/modules
RUN git clone https://github.com/cssrumi/ga-rust.git
WORKDIR /app/modules/ga-rust
RUN pip install --editable .

# Set the working directory to /app
WORKDIR /app/src

# Copy the current directory contents into the container at /app
ADD src /app/src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 755 /app/src/app.py

CMD ["pypy3", "-u", "app.py"]
