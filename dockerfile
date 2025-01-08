# FROM python:3
# RUN pip install waitress
# RUN pip install flask
# RUN pip install google-api-python-client  
# RUN pip install pytz
# RUN mkdir -p /app 
# COPY ./ /app
# WORKDIR /app
# EXPOSE 5000
# # Run your application
# CMD ["python", "app.py"]

FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"
# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "app.py"]

#image name -> python:pay
