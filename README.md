# Develop AWS Glue jobs locally using Docker containers and Python

Container that has _AWS Glue_ under the _Apache Maven_ and _Spark_ for developing with *Python* language usage.

## Installation

1. `git clone https://github.com/zagovorichev/aws-glue-docker.git`
2. `cd aws-glue-docker`
3. `docker-compose up -d`
4. `docker exec -it aws-glue-container /bin/bash /root/bin/install.sh`