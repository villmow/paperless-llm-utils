FROM python:3.12

WORKDIR /usr/src/app

# Install Cron
RUN apt-get update && apt-get -y install cron

# Copy the requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and other necessary files
COPY src/ ./src/
COPY crontab /etc/cron.d/crontab
COPY prompts/ ./prompts/

RUN chmod 0644 /etc/cron.d/crontab
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/crontab

# Execute the script and then start cron job
CMD python src/main.py && cron && tail -f /var/log/cron.log