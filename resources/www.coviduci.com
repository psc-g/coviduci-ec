upstream tornadoserver {
        server localhost:8888;
}
server {
    server_name www.coviduci.com;
    access_log /var/log/nginx/myapp.log;
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-Ip $remote_addr;
        proxy_pass http://tornadoserver;
    }
    listen 443 ssl; # managed by Certbot
    #ssl_certificate /etc/letsencrypt/live/www.coviduci.com/fullchain.pem; # managed by Certbot
    #ssl_certificate_key /etc/letsencrypt/live/www.coviduci.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot



}
server {
    if ($host = www.coviduci.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
    listen 80;
    server_name www.coviduci.com;
    return 404; # managed by Certbot
}
