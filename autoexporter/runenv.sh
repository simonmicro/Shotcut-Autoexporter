docker build -t flaskify .

docker run -p 5000:5000 -v /tmp:/tmp -v $(pwd):/workshop -it flaskify
