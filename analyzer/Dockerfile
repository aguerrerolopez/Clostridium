FROM python:3.11-slim
ARG UNAME=analyzer
ARG PUID
ARG PGID

# Install dependencies
COPY ./requirements.txt /var/tmp/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends r-base-dev libxml2-dev \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && Rscript -e 'install.packages(c("MALDIquant", "MALDIquantForeign", "stringr"), repos="https://cloud.r-project.org")' \
    && pip install -r /var/tmp/requirements.txt \
    && rm /var/tmp/requirements.txt

# Setup non-privileged user
RUN groupadd -o -r -g $PGID $UNAME \
    && useradd -o -r -m -u $PUID -g $PGID $UNAME
USER $UNAME

# Copy and install app
WORKDIR /app
COPY --chown=$PUID:$PGID . .

# Change default command
CMD ["python", "start.py"]
