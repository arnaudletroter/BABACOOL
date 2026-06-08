FROM --platform=linux/amd64 debian:12-slim

LABEL maintainer="arnaud.le-troter@univ-amu.fr"
LABEL description="babacool"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    ca-certificates \
    wget \
    bzip2 \
    git \
    git-annex \
    python3 \
    python3-pip \
    python3-venv \
    libstdc++6 \
    libgomp1 \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxt6 \
    libsm6 \
    libice6 \
    zlib1g \
    libblas3 \
    liblapack3 \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

#FSL_6.0.7.6
COPY fsl_minimal /opt/FSL

#ANTS 2.4
COPY ants_minimal /opt/ANTS

#Convert3D 1.4
COPY Convert3D /opt/Convert3D

COPY babacool /babacool

ENV ANTSPATH=/opt/ANTS/bin
ENV FSLDIR=/opt/FSL/
ENV PATH=$ANTSPATH:$FSLDIR/bin:/opt/Convert3D:$PATH
ENV FSLDIR=/opt/FSL
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV LD_LIBRARY_PATH=$FSLDIR/lib:$LD_LIBRARY_PATH

#RUN pip3 install --no-cache-dir datalad

COPY requirements.txt /tmp/requirements.txt

# Environnement virtuel
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer datalad + requirements
RUN pip install --no-cache-dir datalad
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

#minimal FS (mri_convert)
COPY freesurfer_minimal /opt/FS
# Variables FreeSurfer
ENV FREESURFER_HOME=/opt/FS
ENV PATH=$FREESURFER_HOME:$PATH

COPY freesurfer_minimal/license_FS.txt /opt/FS/.license

WORKDIR /babacool

CMD ["bash"]
