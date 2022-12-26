FROM <use miniconbda image for here> AS build

RUN apt-get update && apt-get install gcc -y

COPY environment.yaml .
RUN conda env create -f environment.yaml

RUN conda install -c conda-forge conda-pack

RUN conda-pack -n bq_metadata -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

RUN /venv/bin/conda-unpack

FROM google/cloud-sdk:latest AS runtime

RUN apt-get update && \
    apt-get install wget -y && \
    apt-get install git -y && \
    apt-get install curl -y && \
    apt-get install jq -y

WORKDIR /app

COPY --from=build /venv /venv
COPY . .

SHELL ["/bin/bash", "-c"]
RUN ["chmod", "+x", "scripts/entry.sh"]
ENTRYPOINT ["echo started"]
