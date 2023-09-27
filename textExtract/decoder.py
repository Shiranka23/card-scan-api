import six
import imghdr
from uuid import uuid4
from base64 import b64decode
from django.core.files.base import ContentFile


def decode_base64_file(data):

        def get_file_extension(file_name, decoded_file):
            extension=imghdr.what(file_name, decoded_file)
            extension='jpg' if extension=='jpeg' else extension
            return extension
        
         # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data=data.split(';base64,')

            # try to decode the file. Return validation error if is false
            try:
                decoded_file=b64decode(data)
            except TypeError:
                TypeError('invalid_image')
            
            # generate filename
            file_name=str(uuid4().hex)

            # get the file extansion
            file_extension=get_file_extension(file_name,decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension)

            file=ContentFile(decoded_file, name=complete_file_name)
            return file,complete_file_name