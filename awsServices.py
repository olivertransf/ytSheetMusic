"""Local stub — original repo uploaded frames/PDFs to S3; we keep everything on disk."""

from collections import defaultdict


class _LocalBucket:
    name = "local"


bucket = _LocalBucket()


def uploadFile(filename, bucket, pdf=False):
    print(f"[local] skip upload: {filename}")


def downloadFile(filename, destination, bucket):
    raise FileNotFoundError(
        f"Local mode: cannot download {filename} from S3. "
        "Ensure frames already exist on disk."
    )


def deleteFile(filename, bucket_name="local"):
    print(f"[local] skip delete: {filename}")


def getFiles(bucket, prefix=""):
    return dict(defaultdict(list))
