# Source for /etc/nginx/sites-enabled/django
# Be sure to change /home/django/WearHacks-Website 
server {
    listen 80;
    server_name montreal.wearhacks.com;
    rewrite ^/(.*) https://montreal.wearhacks.com/$1 permanent;
}

upstream app_server {
    server 127.0.0.1:9000 fail_timeout=0;
}

server {
#    listen 80 default_server;
#    listen [::]:80 default_server ipv6only=on;
    listen 443 ssl;

    root /usr/share/nginx/html;
    index index.html index.htm;

    client_max_body_size 4G;
    server_name montreal.wearhacks.com;
    ssl_certificate /home/ssl/montreal.wearhacks.com.chained.crt;
    ssl_certificate_key /home/ssl/montreal.wearhacks.com.key;

    keepalive_timeout 5;

    # Your Django project's media files - amend as required
    location /media  {
        alias DJANGO_PROJECT_PATH/media;
    }

    # your Django project's static files - amend as required
    location /static {
        alias DJANGO_PROJECT_PATH/assets; 
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app_server;
    }
}