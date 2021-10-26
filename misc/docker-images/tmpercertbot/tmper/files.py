import boto

conn = boto.connect_s3()
bucket = bt.get_bucket('tmpr.py')

"""
NOTES:

    * set Content-Disposition and Expires

    from email.utils import formatdate
    print formatdate(timeval=None, localtime=False, usegmt=True)

    * http://boto.cloudhackers.com/en/latest/s3_tut.html#setting-getting-metadata-values-on-key-objects
    * http://stackoverflow.com/questions/10044151/how-to-generate-a-temporary-url-to-upload-file-to-amazon-s3-with-boto-library

"""
