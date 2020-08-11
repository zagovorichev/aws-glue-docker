FROM ubuntu:18.04

# Dependencies needed for packages downstream
RUN apt-get update && apt-get install -y python3.6 wget python3-pip openjdk-8-jdk git zip && \
	rm -rf /var/lib/apt/lists/*

RUN chmod 0777 /tmp/

# Java
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# All pathes that will be created on build
ENV PATH="/root/lib/apache-maven-3.6.0/bin:$PATH"
ENV SPARK_HOME="/root/lib/spark-2.4.3-bin-hadoop2.8"
ENV SPARK_CONF_DIR=/root/lib/aws-glue-libs/conf
ENV PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}python/lib/py4j-0.10.7-src.zip:/root/lib/aws-glue-libs/PyGlue.zip:${PYTHONPATH}"
ENV PATH="/root/lib/aws-glue-libs/bin:$PATH"
ENV AWS_REGION=eu-west-1
ENV AWS_DEFAULT_REGION=eu-west-1

# Apache Maven
WORKDIR /root/src/
RUN wget https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz

# Apache Spark
WORKDIR /root/src/
RUN wget https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-1.0/spark-2.4.3-bin-hadoop2.8.tgz

# DEBUG
ARG CACHEBUST=1
RUN printenv

# AWS Glue libraries
WORKDIR /root/src/
RUN git clone https://github.com/awslabs/aws-glue-libs.git
