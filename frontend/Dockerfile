FROM node:22.19.0-bullseye-slim

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl vim \
    && apt-get install -y --reinstall procps

COPY ./frontend/package.json /code
RUN npm install

COPY .env /code
COPY ./frontend /code

EXPOSE 3000

CMD ["sleep", "infinity"]
