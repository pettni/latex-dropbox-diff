import os
import sys
import threading
import webbrowser
import time
import logging
from flask import Flask, request, redirect, session
import argparse

import dropbox
from dropbox.exceptions import *

from latex import run_latexdiff

APP_KEY = 'dnu3g85bhjd4np8'
APP_SECRET = 'ut10a8pghd6pjik'
PORT = 65011
TOKEN = None
TOKEN_FILENAME = '.dropbox_token'

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = 'COUCHPOTATO'

def get_dropbox_auth_flow(web_app_session):
    redirect_url = "http://localhost:%s/dropbox-auth-finish" % PORT
    return dropbox.DropboxOAuth2Flow(
        APP_KEY, APP_SECRET, redirect_url, web_app_session,
        "dropbox-auth-csrf-token")


# URL handler for /notapproved
@app.route("/notapproved")
def notapproved():
    return "Request not approved"


# URL handler for /dropbox-auth-start
@app.route("/dropbox-auth-start")
def dropbox_auth_start():
    authorize_url = get_dropbox_auth_flow(session).start()
    return redirect(authorize_url)


# URL handler for /dropbox-auth-finish
@app.route("/dropbox-auth-finish")
def dropbox_auth_finish():
    global TOKEN
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        access_token, user_id, url_state = \
            get_dropbox_auth_flow(session). \
            finish({'code': code, 'state': state})
    except dropbox.oauth2.BadRequestException, e:
        http_status(400)
    except dropbox.oauth2.BadStateException, e:
        # Start the auth flow again.
        return redirect("/dropbox-auth-start")
    except dropbox.oauth2.CsrfException, e:
        http_status(403)
    except dropbox.oauth2.NotApprovedException, e:
        flash('Not approved?  Why not?')
        return redirect("/notapproved")
    except dropbox.oauth2.ProviderException, e:
        logger.log("Auth error: %s" % (e,))
        http_status(403)

    TOKEN = access_token
    request.environ.get('werkzeug.server.shutdown')()  # shut down server
    return '<h1>Thank you</h1>'


def dropbox_authorize_flask():
    global TOKEN

    if os.path.isfile(TOKEN_FILENAME):
        # if there is no access token saved
        f = open(TOKEN_FILENAME, 'r')
        TOKEN = f.read()
        f.close()
    else:
        def open_browser():
            webbrowser.open("http://localhost:%s/dropbox-auth-start" % PORT)

        threading.Timer(0.5, open_browser).start()  # small delay to start
        app.run(debug=False, port=PORT)

        while TOKEN is None:
            time.sleep(1)
        f = open(TOKEN_FILENAME, 'w')
        f.write(TOKEN)
        f.close()


def main(argv):
    # xString = raw_input("Enter the name of the file: ")
    # date_entry = raw_input("Enter a date in YYYY-MM-DD format: ")
    # year, month, day = map(int, date_entry.split('-'))
    # date1 = datetime.date(year, month, day)

    # Parse inputs
    description = 'Highlight changes since last revision'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('filename', action='store', help='Dropbox location of file (e.g. \'/folder/file.tex\')')

    pr = parser.parse_args()
    # filename = '/TEST/cow.tex'

    dropbox_authorize_flask()

    # Connect to dropbox
    dbx = dropbox.Dropbox(TOKEN)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except AuthError:
        sys.exit("ERROR: Invalid access token.")

    list_all = sorted(dbx.files_list_revisions(pr.filename, limit=100).entries,
                      key=lambda entry: entry.server_modified)

    cached_users = {}

    def get_username(user_id):
        if user_id in cached_users:
            return cached_users['id']
        # Get from Dropbox
        account = dbx.users_get_account(user_id)
        cached_users['user_id'] = account.name.given_name
        return cached_users['user_id']

    for i in range(len(list_all)):
        print('%d. %s by %s' %
              (i + 1, list_all[i].server_modified,
               get_username(list_all[i].sharing_info.modified_by)))
    comp_rev = int(raw_input("Select the revision to compare against: "))

    # Download current version
    md1, res1 = dbx.files_download(pr.filename)

    # Download comparison version
    md2, res2 = dbx.files_download('rev:%s' % list_all[comp_rev - 1].rev)

    # Run diff on files
    run_latexdiff(res2.content, res1.content)


if __name__ == "__main__":
    main(sys.argv)
