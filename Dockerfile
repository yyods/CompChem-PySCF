FROM python:3.10-slim

# System deps kept minimal; wheels cover BLAS/libxc for PySCF.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Pin exact versions for reproducibility
ENV PIP_NO_CACHE_DIR=1
RUN pip install --upgrade pip && \
    pip install "numpy==1.26.4" "scipy==1.13.1" \
                "pyscf==2.4.0" "geometric==1.0.0" "pyberny==0.6.3" \
                "fastapi==0.141.1" "uvicorn==0.52.4" "pydantic==2.13.4"

# No Qt here on purpose: the desktop client runs on the HOST and reaches this
# service over HTTP. That split is the point of the Service-Runner pattern.

# Runtime workspace - no scripts embedded for live development
WORKDIR /workspace
RUN mkdir -p /workspace/results /workspace/scripts /workspace/jobs

# Cross-platform entrypoint
ENTRYPOINT ["/usr/local/bin/python"]
