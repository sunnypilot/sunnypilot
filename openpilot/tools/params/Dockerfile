FROM debian:bookworm-slim@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++=4:12.2.0-3 g++-12=12.2.0-14+deb12u1 gcc-12=12.2.0-14+deb12u1 \
    libstdc++-12-dev=12.2.0-14+deb12u1 libc6-dev=2.36-9+deb12u14 \
    binutils=2.40-2 python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
