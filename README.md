# Getting started #

## Use the official image ##
You'll need the `docker-compose.yml` file, then just type `docker-compose up` to start directly (using the official image `realsimonmicro/shotcut-autoexporter`. Enjoy!

## Build it yourself! ##
Replace the `image:` key inside the `docker-compose.yml` to `build: .`, then just build the container (with `docker-compose build`) and start it like the example above. You may append `--build` to rebuild the container on start, when needed!
