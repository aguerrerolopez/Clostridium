FROM php:8.2-fpm-alpine
ARG HOSTNAME
RUN apk --no-cache add curl libzip-dev tzdata supervisor nginx \
    && docker-php-ext-install mysqli zip \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Copy app
COPY --chmod=755 . /app
WORKDIR /
RUN composer install --working-dir=/app --no-dev --optimize-autoloader \
    && mv /app/nginx.conf /etc/nginx/nginx.conf \
    && mv /app/php.ini /usr/local/etc/php/conf.d/zz-docker.ini \
    && mv /app/www.conf /usr/local/etc/php-fpm.d/zz-docker.conf

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]
