docker build -t flaskify .

docker run -p 5000:5000 -v $(pwd):/workshop -it flaskify
