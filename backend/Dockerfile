FROM python:3.12-alpine

ENV MONGO_DB_USERNAME=admin \
    MONGO_DB_PWD=password 
    
    ##mongodb_uri=mongodb://admin:password@localhost:27017

WORKDIR /home/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 
    ## . /home/app ile aynı anlama geliyor

EXPOSE 8000
##container build ettikten sonra run ederken -p 8000:8000 ile portu eşleştirmemiz gerekiyor.

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]