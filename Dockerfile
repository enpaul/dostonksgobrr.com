# ============================================
#   STAGE 0 - Prebuild Image
# ============================================
FROM python:3.9 as BUILDER

# Install buildtime dependencies
RUN apt update --yes
RUN apt upgrade --yes
RUN mkdir /build
RUN python -m pip install pip==19.3.1 \
  --upgrade \
  --disable-pip-version-check
RUN curl -o /build/get-poetry.py -sSL \
  https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py
# Put poetry in the root instead of the user home
ENV POETRY_HOME /build/poetry
RUN python /build/get-poetry.py

# Copy the local source code into the container
ADD . /build/install
WORKDIR /build/install

# Generate the requirements.txt file from the poetry lockfile
RUN /build/poetry/bin/poetry export \
  --extras deploy \
  --format requirements.txt \
  --output /build/req.txt \
  --without-hashes

# Download and build the wheels using the requirements file
RUN python -m pip wheel \
  --wheel-dir /build/wheels \
  --requirement /build/req.txt \
  --disable-pip-version-check \
  --no-cache-dir

# Build the wheel for the local project and put it with the downloaded wheels
RUN /build/poetry/bin/poetry build --format wheel
RUN mv /build/install/dist/*.whl /build/wheels/

# ============================================
#   STAGE 1 - Deployment Image
# ============================================
# The deployment container is pulled from the python:3.7-slim container because the folks that
# build it are way better at packaging python compactly than I am
FROM python:3.9-slim

# Setup container filesystem and settings
RUN apt update --yes && \
  apt clean --yes && \
  groupadd stonks --gid 999 --system && \
  useradd stonks --uid 999 --no-log-init --system --gid stonks && \
  mkdir /app && \
  chown -R stonks:stonks /app

# Copy the prebuilt wheels from stage 0 into this stage, install them, then delete the temporary
# wheel directory
COPY --from=BUILDER /build/wheels /install/wheels
RUN python -m pip install dostonksgobrr[deploy] \
  --upgrade \
  --pre \
  --no-index \
  --no-cache-dir \
  --find-links /install/wheels \
  --disable-pip-version-check && \
  rm -rf /install/

# Run as not-root, because Best Practices
USER stonks:stonks

CMD [ \
  "gunicorn", \
  "dostonksgobrr.application:APPLICATION", \
  "--timeout=30", \
  "--bind=0.0.0.0:8080", \
  "--workers=8", \
  "--log-level=info", \
  "--access-logfile=-" \
]
