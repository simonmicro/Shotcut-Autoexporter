docker build -t flaskify .

docker run -v $(pwd):/workshop -it flaskify
