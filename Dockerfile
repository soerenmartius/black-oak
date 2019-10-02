FROM python:3.7-stretch

# install some tools we need for debugging
RUN apt-get update && \
    apt-get install -y vim htop && \
    rm -rf /var/lib/apt/lists/*

# set workdir
WORKDIR /usr/src/app

# create data dir
RUN mkdir data

# install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# source code and config
COPY . .

# set cmd
CMD [ "python", "fetch_ohlcv_data.py", "config.toml" ]

