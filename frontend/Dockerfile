FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Statik frontend dosyalarını (index.html, script.js, style.css vs.) kopyala
COPY . /usr/share/nginx/html

# Nginx'in kendi config'ini, bizim reverse-proxy ayarımız olan nginx.conf ile değiştir
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5500
## container build ettikten sonra run ederken -p 5500:5500 ile portu eşleştirmemiz gerekiyor.

# nginx image'i zaten kendi CMD'siyle (nginx -g 'daemon off;') foreground'da çalışıyor,
# ayrıca bir CMD belirtmemize gerek yok.