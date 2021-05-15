FROM python:3.9-alpine
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python","main.py","-s","${PIXVIID}","t","${TAGS}","-w","${DISCORDHOOK}"]