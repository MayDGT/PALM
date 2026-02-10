FROM python:3.9-slim

# ---------- system deps ----------
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# ---------- fix pip / setuptools ----------
RUN pip install --upgrade \
    pip==23.0.1 \
    setuptools==65.5.1 \
    wheel

# ---------- clone Aerialist ----------
RUN git clone https://github.com/skhatiri/Aerialist.git \
    && cd Aerialist \
    && git checkout v1.0 \
    && pip install --no-cache-dir \
         -i https://pypi.tuna.tsinghua.edu.cn/simple \
         -r requirements.txt \
    && cp template.env .env \
    && sed -i 's|DOCKER_IMG=.*|DOCKER_IMG=skhatiri/aerialist:1.0|' .env \
    && mkdir -p results

# ---------- clone PALM into Aerialist/samples ----------
WORKDIR /workspace/Aerialist/samples
RUN git clone https://github.com/MayDGT/PALM.git

WORKDIR /workspace/Aerialist/samples/PALM
RUN mkdir -p logs results generated_tests

ENTRYPOINT ["python", "main.py"]
