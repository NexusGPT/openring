FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake git ca-certificates libhdf5-dev libboost-all-dev libtinyxml-dev zlib1g-dev python3-pip python3-venv python3-dev && rm -rf /var/lib/apt/lists/*
RUN git clone --recursive https://github.com/thliebig/openEMS-Project.git /src/openEMS-Project && git -C /src/openEMS-Project rev-parse HEAD > /src/openems-project-head.txt
RUN cd /src/openEMS-Project && ./update_openEMS.sh /opt/openEMS --python --disable-GUI --njobs 8 --verbose
RUN /opt/openEMS/venv/bin/pip3 install scipy
ENV PATH="/opt/openEMS/bin:/opt/openEMS/venv/bin:${PATH}"
