FROM python:3.7-stretch

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /code/

WORKDIR /code/

RUN pip install -r requirements.txt

COPY . /code/
EXPOSE 8000

ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["python", "/code/manage.py", "runserver", "0.0.0.0:8000"]