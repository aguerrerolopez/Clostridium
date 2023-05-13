FROM php:8.2-fpm-alpine
ARG HOSTNAME
RUN apk --no-cache add curl libzip-dev tzdata supervisor nginx \
    && docker-php-ext-install mysqli zip \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Copy app
COPY . /app
WORKDIR /
RUN composer install --working-dir=/app --no-dev --optimize-autoloader \
    && mv /app/nginx.conf /etc/nginx/nginx.conf \
    && mv /app/php-custom.ini $PHP_INI_DIR/conf.d/zz-custom.ini

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]
