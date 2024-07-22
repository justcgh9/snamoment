FROM python:3.10-slim


RUN apt-get update && apt-get install -y \
    imagemagick\
    ffmpeg\
    && apt-get clean

COPY ./policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt


# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt


COPY . /app

CMD ["python3", "app.py"]