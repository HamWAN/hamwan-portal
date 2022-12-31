# syntax=docker/dockerfile:1.4
ARG PYTHON_VERSION=2.7
FROM python:$PYTHON_VERSION
EXPOSE 8000
WORKDIR /app 
COPY requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app 
ENTRYPOINT ["python"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
