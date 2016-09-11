import os
import sys

import dropbox
from dropbox.exceptions import AuthError


def dropbox_authorize():
    """Obtain Dropbox access token"""

    token_filename = '.dropbox_token'

    if os.path.isfile(token_filename):
        # if there is no access token saved
        f = open(token_filename, 'r')
        access_token = f.read()
        f.close()
    else:
        # Get your app key and secret from the Dropbox developer website
        app_key = 'dnu3g85bhjd4np8'
        app_secret = 'ut10a8pghd6pjik'

        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        # Have the user sign in and authorize this token
        authorize_url = flow.start()
        print '1. Go to: ' + authorize_url
        print '2. Click "Allow" (you might have to log in first)'
        print '3. Copy the authorization code.'
        code = raw_input("Enter the authorization code here: ").strip()

        # This will fail if the user enters an invalid authorization code
        access_token, user_id = flow.finish(code)

        # save it
        f = open(token_filename, 'w')
        f.write(access_token)
        f.close()

    return access_token


def get_files(filename, date):
    """ Get old version of file"""

    access_token = dropbox_authorize()

    # connect to dropbox
    dbx = dropbox.Dropbox(access_token)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
        print "Connection successful"
    except AuthError:
        sys.exit("ERROR: Invalid access token.")

    first_ver = sorted(dbx.files_list_revisions(filename, limit=30).entries,
                       key=lambda entry: entry.server_modified)[0]

    # Download current version
    md1, res1 = dbx.files_download(filename)

    # Download old version
    md2, res2 = dbx.files_download(filename, first_ver.rev)

    print "Current version:"
    print res1.content
    print "\n"
    print "Old version:"
    print res2.content
