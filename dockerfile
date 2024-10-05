FROM python:3
RUN pip install waitress
RUN pip install flask
RUN pip install google-api-python-client  
RUN mkdir -p /app 
COPY ./ /app
WORKDIR /app
EXPOSE 5000
# Run your application
CMD ["python", "app.py"]
