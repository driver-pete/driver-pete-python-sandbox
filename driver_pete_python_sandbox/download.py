
import os
from boto.s3.connection import S3Connection
import ConfigParser
from StringIO import StringIO


class S3(object):
    '''
    Expects security.properties file in the same folder with the following content:
    AWS_ACCESS_KEY_ID=<YOUR KEY ID>
    AWS_SECRET_KEY=<YOUR KEY>
    '''
    def __init__(self, bucket_name):    
        security_file = os.path.join(os.path.dirname(__file__), 'security.properties')
        if not os.path.exists(security_file):
            raise Exception("Please put security.properties file in the same folder with this script")
        
        #http://stackoverflow.com/questions/9686184/is-there-a-version-of-configparser-that-deals-with-files-with-no-section-headers
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO(u'[DUMMY]\n%s'  % open(security_file).read()))
        config = dict(config.items('DUMMY'))

        self._connection = S3Connection(config['aws_access_key_id'], config['aws_secret_key'])
        self._bucket = self._connection.get_bucket(bucket_name)
    
    def list_keys(self):
        return [l for l in self._bucket.get_all_keys()]
     
    def download(self, key_name, download_folder):
        k = self._bucket.get_key(key_name)
        result_filename = os.path.join(download_folder,
                                       os.path.split(key_name)[-1])
        k.get_contents_to_filename(result_filename)

    def download_folder(self, s3_folder, results_folder):
        assert(os.path.exists(results_folder))
        for k in self._bucket.get_all_keys(prefix=s3_folder):
            #http://stackoverflow.com/questions/9954521/s3-boto-list-keys-sometimes-returns-directory-key
            if k.name in [s3_folder, s3_folder+'/']:
                continue
            result_filename = os.path.join(results_folder,
                                           os.path.split(k.name)[-1])
            k.get_contents_to_filename(result_filename)


if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts/raw')
    if not os.path.exists(artifacts):
        os.mkdir(artifacts)

    s3 = S3('driverpete-storage')
    s3.download_folder('Oleg', artifacts)
    