import os
import sys

import dropbox
from dropbox.exceptions import AuthError

from latex import run_latexdiff


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


def main(argv):
    # xString = raw_input("Enter the name of the file: ")
    # date_entry = raw_input("Enter a date in YYYY-MM-DD format: ")
    # year, month, day = map(int, date_entry.split('-'))
    # date1 = datetime.date(year, month, day)

    filename = '/TEST/test1.tex'

    access_token = dropbox_authorize()

    # Connect to dropbox
    dbx = dropbox.Dropbox(access_token)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
        print "Connection successful"
    except AuthError:
        sys.exit("ERROR: Invalid access token.")

    list_all = sorted(dbx.files_list_revisions(filename, limit=30).entries,
                      key=lambda entry: entry.server_modified)

    for i in range(len(list_all)):
        # print i + 1, '. ', list_all[i].server_modified
        print('%d. %s' % (i + 1, list_all[i].server_modified))

    xString = raw_input("Select the version to be compared: ")
    first_ver = int(xString)

    # Download current version
    md1, res1 = dbx.files_download(filename)

    # Download old version
    md2, res2 = dbx.files_download(filename, list_all[first_ver - 1].rev)

    run_latexdiff(res1, res2)

    pass


if __name__ == "__main__":
    main(sys.argv)
