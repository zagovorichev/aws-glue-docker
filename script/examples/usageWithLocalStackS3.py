sc = SparkContext()
        self.__glue_context: GlueContext = GlueContext(sc)
        self.__spark = self.__glue_context.spark_session

        # if self.get_env() == 'dev':
        if True:
            # self.__spark.sparkContext.setLogLevel("DEBUG")

            # Setup spark to use s3, and point it to the correct server.
            hadoop_conf = self.__spark.sparkContext._jsc.hadoopConfiguration()
            hadoop_conf.set("fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            hadoop_conf.set("fs.s3a.access.key", "mock")
            hadoop_conf.set("fs.s3a.secret.key", "mock")
            # dockerized environment
            hadoop_conf.set("fs.s3a.endpoint", "host.docker.internal:4572")
            # non dockerized
            # hadoop_conf.set("fs.s3a.endpoint", "localstack.docker.localhost:4572")
            hadoop_conf.set('fs.s3a.path.style.access', 'true')
            hadoop_conf.set('fs.s3a.connection.ssl.enabled', 'false')

data_frame.write \
            .mode('overwrite') \
            .csv(
                's3://tmp_output_dir',
                compression="gzip",
                sep=";",
                header=True,
                ignoreTrailingWhiteSpace=True,
            )