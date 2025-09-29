# Stage 1: Build dependencies into /dep
FROM python:3.11-alpine AS builder
WORKDIR /app
RUN apk add --no-cache build-base linux-headers gcc musl-dev libffi-dev openssl-dev

COPY App/requirement.txt /app

RUN pip install --no-cache-dir --prefix=/dep -r requirement.txt && \
    rm -rf requirement.txt

COPY App/app.py /app/

# Stage 2: Runtime as Alpine
FROM python:3.11-alpine AS runtime
WORKDIR /app
RUN apk add --no-cache libstdc++ libgcc shadow

COPY --from=builder /dep /usr/local
COPY --from=builder /app/app.py /app/app.py
RUN addgroup --gid 1001 appadmingroup && \
    useradd -m -u 1001 -g appadmingroup appadmin && \
    chown -R appadmin:appadmingroup /app 

ENV PYTHONPATH=/dep
USER appadmin
EXPOSE 5000
CMD ["python3", "/app/app.py"] 

# Stage 3: Debug as root
FROM python:3.11-alpine AS debug
WORKDIR /app
RUN apk add --no-cache libstdc++ libgcc shadow

COPY --from=builder /dep /usr/local
COPY --from=builder /app/app.py /app/app.py


ENV PYTHONPATH=/dep
USER root
EXPOSE 5000
CMD ["python3", "/app/app.py"]
