# Develop AWS Glue jobs locally using Docker containers and Python

Container that has _AWS Glue_ under the _Apache Maven_ and _Spark_ for developing with *Python* language usage.

## Installation

1. `git clone https://github.com/zagovorichev/aws-glue-docker.git`
2. `cd aws-glue-docker`
3. `docker-compose up -d`
4. `docker exec -it aws-glue-container /bin/bash /root/bin/install.sh`

## Test

### Glue Script CSV

```shell script
docker exec -it aws-glue-container /bin/bash
$SPARK_HOME/bin/spark-submit --master local\[1\] $HOME/script/glue_script.py --JOB_NAME local_test
```