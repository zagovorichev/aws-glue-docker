report_date = datetime.datetime.now().strftime("%Y%m%d")
output_bucket = 'aws-glue-temporary-000000000-eu-west-3'
output_dir = 'dir/exports/{}/rds'.format(context.get_argument_service().get_report_code())
tmp_output_dir = 'dir/tmp/exports/{}/rds'.format(context.get_argument_service().get_report_code())
report_name = "results.csv.gz"
tmp_output_dir = '{}/{}'.format(tmp_output_dir, report_date)
data_frame.write.csv(
    's3://{}/{}'.format(output_bucket, tmp_output_dir),
    compression="gzip",
    sep=";",
    header=True,
    ignoreTrailingWhiteSpace=True
)

# Move output file to file with required path and name
report_name = '{}_{}'.format(report_date, report_name)
s3_client = boto3.client('s3')
report_files = s3_client.list_objects(
    Bucket=output_bucket,
    Prefix=tmp_output_dir,
)
tmp_report_name = report_files["Contents"][0]["Key"]
s3_client.copy_object(
    Bucket=output_bucket,
    CopySource='{}/{}'.format(output_bucket, tmp_report_name),
    Key='{}/{}'.format(output_dir, report_name)
)
s3_client.delete_object(Bucket=output_bucket, Key=tmp_report_name)