FROM php:8.2-fpm-alpine
ARG HOSTNAME
RUN apk --no-cache add caddy curl libzip-dev supervisor tzdata \
    && caddy add-package github.com/caddyserver/transform-encoder \
    && docker-php-ext-install mysqli zip \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Copy app
COPY --chmod=755 . /app
WORKDIR /
RUN composer install --working-dir=/app --no-dev --optimize-autoloader \
    && chmod +x /app/entrypoint.sh \
    && mv /app/Caddyfile /etc/caddy/Caddyfile \
    && mv /app/php.ini /usr/local/etc/php/conf.d/zz-docker.ini \
    && mv /app/www.conf /usr/local/etc/php-fpm.d/zz-docker.conf

ENTRYPOINT ["/app/entrypoint.sh"]
