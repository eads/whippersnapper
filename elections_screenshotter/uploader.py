import logging
import util

from boto.s3.connection import Key, S3Connection

class Uploader(object):
    """
    Implements all upload-related logic.
    """

    def __init__(self, config):
        self.config = config
        conn = S3Connection(self.config.get('aws_access_key'),
                self.config.get('aws_secret_key'))

        # The bucket must already exist.
        self.bucket = conn.get_bucket(self.config.get('aws_bucket'))

    def upload_screenshots(self, images):
        """
        Runs through the process of uploading all screenshots.

        Uploads each image to both its filepath and the "latest" filepath.
        """
        filepaths = []
        for image in images:
            filepaths.append(self.upload(image.get('local_filepath'),
                    image.get('aws_filepath')))
            logging.info('Sucessfully uploaded image to %s' % (filepaths[-1]))

            filepaths.append(self.upload(image.get('local_filepath'),
                    image.get('aws_latest_filepath')))
            logging.info('Sucessfully uploaded image to %s' % (filepaths[-1]))
        return filepaths

    def upload(self, local_filepath, aws_filepath):
        """
        Uploads `local_filepath` to `aws_filepath`.

        Returns the published URL for the file.
        """
        logging.info('Publishing %s to %s' % (
                local_filepath, aws_filepath))

        key = Key(bucket=self.bucket, name=aws_filepath)
        key.key = aws_filepath
        key.set_contents_from_filename(local_filepath)
        key.set_acl('public-read')
        return util.generate_public_url(self.config.get('aws_bucket'),
                aws_filepath)
