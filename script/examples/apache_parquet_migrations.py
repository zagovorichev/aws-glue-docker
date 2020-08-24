import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
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
        self._args = {'TempDir': 's3://link/temp',
                      'JOB_NAME': 'z-etl-test',
                      'OutputPath': 's3://link/output'}


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


class ReadDynamicDataFromDatabase(ReadDynamicDataFromLocalStorage):
    def _set_variable_dynamic_frame(self, context: ContextService):
        self._variable_storage_dynamic_frame = context.get_glue_context().create_dynamic_frame.from_catalog(
            database='dbname',
            table_name='variable_storage',
            redshift_tmp_dir=context.get_argument_service().get_temp_dir(),
            transformation_ctx='variable_storage_dynamic_frame'
        )

    def _set_result_dynamic_frame(self, context: ContextService):
        self._result_storage_dynamic_frame = context.get_glue_context().create_dynamic_frame.from_catalog(
            database='dbname',
            table_name='result_storage',
            redshift_tmp_dir=context.get_argument_service().get_temp_dir(),
            transformation_ctx='result_storage_dynamic_frame'
        )


class WriteDataToApacheParquet():
    @staticmethod
    def store(context: ContextService, dynamic_frame):
        context.get_glue_context().write_dynamic_frame.from_options(
            frame=dynamic_frame,
            connection_type="s3",
            connection_options={"path": "s3://s3link/result_storage"},
            format="parquet")

        context.get_glue_context().write_dynamic_frame.from_options(
            frame=dynamic_frame,
            connection_type="s3",
            connection_options={
                "path": "s3://s3link/variable_storage"},
            format="parquet")


if __name__ == '__main__':
    DebugLogger.log_action('Start time')
    # argument_service = ArgumentService()
    argument_service = ArgumentServiceStatic()
    context_service = ContextService(argument_service)
    # you can read the data from anywhere you want
    dynamic_data_reader = ReadDynamicDataFromLocalStorage(context_service)
    # dynamic_data_reader = ReadDynamicDataFromDatabase(context_service)
    DebugLogger.log_action('Data already read')
    # read dynamic data and write it to the file storage, then we can move and use it for other glue instances
    # development for example
    WriteDataToApacheParquet.store(context_service, dynamic_data_reader)
    DebugLogger.log_action('Data written to the storage')
    DebugLogger.log_action('End time')
    context_service.commit_job()
