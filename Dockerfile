FROM python:3.8
WORKDIR /app
COPY . /app.py
RUN /bin/sh -c pip install -r requirements.txt
EXPOSE 80
CMD ["python", "app.py"]
