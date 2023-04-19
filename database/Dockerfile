FROM mariadb:10.11
ARG UNAME=database
ARG PUID
ARG PGID

# Install Node.js and Yarn
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates wget \
    && wget -qO- https://deb.nodesource.com/setup_18.x | bash - \
    && wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/yarn.gpg \
    && echo 'deb https://dl.yarnpkg.com/debian stable main' | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs yarn \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy app to image
COPY . /app

# Setup non-privileged user
RUN groupadd -o -r -g $PGID $UNAME \
    && useradd -o -r -m -u $PUID -g $PGID $UNAME \
    && chown -R $PUID:$PGID /var/lib/mysql /var/run/mysqld /app \
    && chmod +x /app/*.sh \
    && mv /app/console.sh /usr/local/bin/console \
    && mv /app/run-script.sh /usr/local/bin/run-script
USER $UNAME

# Install app
RUN yarn --cwd /app install --production

# Change default command
CMD ["/app/entrypoint.sh"]
