s3_download_arn='arn:aws:iam::123456789012:role/S3DownloadRole'

case "$1" in

"c")
    python create_jobs.py thing_name thing_arn ${s3_download_arn}
    ;;
"u")
    python create_jobs.py thing_name thing_arn ${s3_download_arn}
    ;;
esac
