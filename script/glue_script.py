# For https://support.wharton.upenn.edu/help/glue-debugging
import uuid
from pyspark.sql.functions import *
from pyspark.sql.types import StringType, IntegerType, StructField, StructType
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
import sys
from pyspark.context import SparkContext
import datetime

NOW_STR = datetime.datetime.now().strftime('%Y-%M-%d__%H_%M_%S_')

# Need a unique directory for each run. S3 can't overwrite datasets.
path_ext = str(uuid.uuid4())
SOURCE_ROOT = "/root/script/input"
OUTPUT_ROOT = "/root/script/output/"
s3_output_path = OUTPUT_ROOT + path_ext + "/"

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

schema = StructType([
    StructField("YEAR", IntegerType(), False),
    StructField("GoogleKnowlege_Occupation", StringType(), False),
    StructField("Show", StringType(), True),
    StructField("Group", StringType(), True),
    StructField("Raw_Guest_List", StringType(), True)
])

df = spark.read.format("com.databricks.spark.csv") \
    .option("header", "true") \
    .option('quote', '"') \
    .option("encoding", "UTF-8") \
    .option("multiLine", "true") \
    .option("escape", "\"") \
    .option("columnNameOfCorruptRecord", "_corrupt_column") \
    .option("mode", "PERMISSIVE") \
    .schema(schema) \
    .csv(SOURCE_ROOT)

df.printSchema()
df.write \
    .parquet(s3_output_path)

# Partitioning not working on limited mac tests
# df.write \
#     .partitionBy("YEAR", "Group") \
#     .parquet(s3_output_path)
