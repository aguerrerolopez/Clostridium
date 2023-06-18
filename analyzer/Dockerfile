FROM python:3.11-alpine
ARG UNAME=analyzer
ARG PUID
ARG PGID

# Setup non-privileged user
RUN addgroup -S -g $PGID $UNAME \
    && adduser -S -D -u $PUID -G $UNAME $UNAME \
    && mkdir /app \
    && chown $PUID:$PGID /app
USER $UNAME

# Copy and install app
WORKDIR /app
COPY --chown=analyzer:analyzer . .
RUN pip install --user -r requirements.txt

# Change default command
CMD ["python", "start.py"]
