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

## Data usage

> How can we access the data to be used in the script.

Useful examples of code:
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
import pyspark.sql.functions as f
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
import datetime

class ArgumentService:
    def __init__(self):
        self._set_args()

    def _set_args(self):
        self._args = getResolvedOptions(sys.argv, ['TempDir', 'JOB_NAME', 'OutputPath'])

    def get_args(self):
        return self._args

    def get_temp_dir(self):
        return self.get_args()['TempDir']

    def get_job_name(self):
        return self.get_args()['JOB_NAME']

    def get_output_path(self):
        return self.get_args()['OutputPath']


class ArgumentServiceStatic(ArgumentService):
    def _set_args(self):
        self._args = {'TempDir': 's3://###/zfolder/temp',
                      'JOB_NAME': 'z-etl-test-tao',
                      'OutputPath': 's3://###/zfolder/output'}

class ContextService:
    def __init__(self, argument_service: ArgumentService):
        sc = SparkContext()
        self.__argument_service = argument_service
        self.__glue_context: GlueContext = GlueContext(sc)
        self.__spark = self.__glue_context.spark_session
        self.__job = Job(self.__glue_context)
        self.__job.init(self.__argument_service.get_job_name(), self.__argument_service.get_args())

    def get_glue_context(self):
        return self.__glue_context

    def get_spark(self):
        return self.__spark

    def commit_job(self):
        return self.__job.commit()

    def get_argument_service(self):
        return self.__argument_service


class DebugLogger:
    @staticmethod
    def log_action(info_message):
        dt_ = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(info_message, ":", dt_)

class ResultService:
    @staticmethod
    def print_result(dynamic_frame: DynamicFrame):
        data_frame = dynamic_frame.toDF()
        data_frame.show(data_frame.count(), False)

    @staticmethod
    def write_result_to_s3_csv(context: ContextService, dynamic_frame: DynamicFrame):
        context.get_glue_context().write_dynamic_frame.from_options(
            frame=dynamic_frame,
            connection_type="s3",
            connection_options={
                "path": context.get_argument_service().get_output_path(),
            },
            format="csv"
        )


class MainTransformer:
    @staticmethod
    def transform(context: ContextService, dynamic_frame: DynamicFrame):
        data_frame = dynamic_frame.toDF()
        # count of values in the table
        # print(dataVariablesFrame.count())
        # print full table
        # dataVariablesFrame.show(dataVariablesFrame.count(), False)

        # Transform
        aggregated_data_frame = data_frame.groupby('field_to_group').agg(
            f.col('field_to_group').alias('field_to_group'),
            f.countDistinct(f.col('to_be_counted')).alias('distinctValOfField'),
        )

        # Store exported data

        # 1 partition - to have only 1 file
        aggregated_data_frame = aggregated_data_frame.repartition(1)

        # Convert to dynamic frame
        return DynamicFrame.fromDF(aggregated_data_frame, context.get_glue_context(), 'write_dynamic_frame')


if __name__ == '__main__':
    DebugLogger.log_action('Start time')

    # argument_service = ArgumentService()
    argument_service = ArgumentServiceStatic()

    context_service = ContextService(argument_service)

    dynamic_data_reader = ReadDynamicDataFromLocalStorage(context_service)
    # dynamic_data_reader = ReadDynamicDataFromDatabase(context)
    # read dynamic data and write it to the file storage, then we can move and use it for other glue instances
    # development for example
    # WriteDataToApacheParquet.store(context_service, dynamic_data_reader);

    source_dynamic_frame = SourceBuilder(dynamic_data_reader.get_variable_dynamic_frame(),
                                         dynamic_data_reader.get_result_dynamic_frame()).joined_storage_dynamic_frame

    DebugLogger.log_action('Dynamic frame created time')

    result_dynamic_frame = MainTransformer.transform(context_service, source_dynamic_frame)

    ResultService.print_result(result_dynamic_frame)
    # ResultService.write_result_to_s3_csv(context_service, result_dynamic_frame)

    DebugLogger.log_action('End time')

    context_service.commit_job()
```

### 

### Data migration for the test

1. Load data from AWS to the Apache Parquet 

```python
class WriteDataToApacheParquet():
    @staticmethod
    def store(context: ContextService, dynamic_frame: DynamicFrame):
        context.get_glue_context().write_dynamic_frame.from_options(
            frame=dynamic_frame,
            connection_type="s3",
            connection_options={"path": "s3://s3path-###-eu-west-3/zfolder/export/result_storage"},
            format="parquet")
```

2. Download these files to the local directory and you can connect this storage as a DynamicFrame
```python
class ReadDynamicDataFromLocalStorage:
    def __init__(self, context: ContextService):
        self._set_result_dynamic_frame(context)
        self._set_variable_dynamic_frame(context)

    def _set_result_dynamic_frame(self, context: ContextService):
        result_storage_data_frame = context.get_spark().read.parquet('./storage/result_storage')
        self._result_storage_dynamic_frame = DynamicFrame.fromDF(result_storage_data_frame, context.get_glue_context(),
                                                                 'result_storage_dynamic_frame')

    def _set_variable_dynamic_frame(self, context: ContextService):
        variable_storage_data_frame = context.get_spark().read.parquet('./storage/variable_storage')
        self._variable_storage_dynamic_frame = DynamicFrame.fromDF(variable_storage_data_frame,
                                                                   context.get_glue_context(),
                                                                   'variable_storage_dynamic_frame')

    def get_result_dynamic_frame(self):
        return self._result_storage_dynamic_frame

    def get_variable_dynamic_frame(self):
        return self._variable_storage_dynamic_frame
```
