FROM python:3.11-slim

# System deps kept minimal; wheels cover BLAS/libxc for PySCF.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Pin exact versions for reproducibility
ENV PIP_NO_CACHE_DIR=1
RUN pip install --upgrade pip && \
    pip install "numpy==1.26.4" "scipy==1.13.1" \
                "pyscf==2.4.0" "geometric==1.0.0" "pyberny==0.6.4"

# Runtime workspace
WORKDIR /work
COPY scripts/ /work/scripts/
ENTRYPOINT ["/usr/local/bin/python"]
