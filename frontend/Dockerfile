FROM python:3.12-alpine

WORKDIR /home/app

COPY . /home/app
    ## . /home/app ile aynı anlama geliyor

EXPOSE 5500
##container build ettikten sonra run ederken -p 5500:5500 ile portu eşleştirmemiz gerekiyor.

CMD ["python", "-m", "http.server", "5500"]