FROM python:3.12-slim AS dbgen
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev make curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://github.com/electrum/tpch-dbgen/archive/32f1c1b92d1664dba542e927d23d86ffa57aa253.zip -o /tmp/dbgen.zip \
    && unzip -q /tmp/dbgen.zip -d /opt && mv /opt/tpch-dbgen-* /opt/tpch-dbgen \
    && cd /opt/tpch-dbgen && make MACHINE=LINUX DATABASE=ORACLE

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client util-linux procps git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "psycopg[binary]==3.2.*" matplotlib==3.9.*
COPY --from=dbgen /opt/tpch-dbgen /opt/tpch-dbgen
WORKDIR /app
COPY src /app/src
COPY queries /app/queries
COPY tests /app/tests
ENV PYTHONPATH=/app/src DSS_QUERY=/opt/tpch-dbgen/queries
