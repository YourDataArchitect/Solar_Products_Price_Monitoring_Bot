# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install system dependencies for Selenium, tzdata for time zone configuration, and locales
RUN apt-get update && apt-get install -y \
    apt-utils \
    lsb-release \
    wget \
    gnupg \
    unzip \
    tzdata \
    libssl-dev \
    liblzo2-dev \
    libpcap0.8-dev \
    iputils-ping \
    curl \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Download and install Surfshark
RUN curl -f https://downloads.surfshark.com/linux/debian-install.sh --output /surfshark-install.sh
RUN sh surfshark-install.sh

# Set the time zone
ENV TZ=Europe/Berlin

# Configure locales
RUN sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen de_DE.UTF-8 && \
    update-locale LANG=de_DE.UTF-8

# Ensure environment variables are set for locale
ENV LANG=de_DE.UTF-8 \
    LANGUAGE=de_DE:de \
    LC_ALL=de_DE.UTF-8

# Add Google's official GPG key and repository
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
    
# Install the latest stable version of Chrome
RUN apt-get update && apt-get install -y google-chrome-stable
    
# Set the working directory in the container
WORKDIR /app

# Copy ChromeDriver files to the Docker image
COPY chromedriver /usr/local/bin/chromedriver
COPY LICENSE.chromedriver /usr/local/bin/LICENSE.chromedriver
COPY THIRD_PARTY_NOTICES.chromedriver /usr/local/bin/THIRD_PARTY_NOTICES.chromedriver

# Set the correct permissions for the ChromeDriver binary
RUN chmod +x /usr/local/bin/chromedriver

# Copy the auth file into the container
COPY auth.txt .


# Copy the requirements file into the container
COPY requirements.txt .

# Update pip
RUN pip install --upgrade pip

# Install the required libraries
RUN for i in $(seq 1 5); do pip install --no-cache-dir -r requirements.txt && break || sleep 5; done

# Copy the rest of the application code into the container
COPY . .

# Set the command to run the application
CMD ["python", "Market_Monitor.py"]
