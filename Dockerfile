FROM nginx:1.27-alpine

COPY stock-buscador.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
