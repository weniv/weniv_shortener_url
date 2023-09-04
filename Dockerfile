FROM python:3.11-alpine

LABEL version="1.0"

MAINTAINER "MAX" <pipiru100@gmail.com>

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libpq-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install dependencies

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip3 install -r requirements.txt

# Copy project

COPY . /usr/src/app/

# Run entrypoint.sh

#ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

RUN python3 manage.py collectstatic --noinput

# Run server
EXPOSE 8000

CMD ["python3", "manage.py", "runserver","0.0.0.0:8000"]


