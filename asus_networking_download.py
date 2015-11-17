#!/usr/bin/env python3
# coding: utf-8
import sqlite3
import ipdb
import traceback
import sys
from ftp_credentials import ftpHostName,ftpUserName,ftpPassword
import ftputil
import urllib
from os import path
import os
from my_utils import uprint
from web_utils import firefox_url_req, urlFileName, downloadFile, \
        safeFileName, getFileSha1, safeUrl

dlDir=path.abspath('firmware_files/')

def main():
    startIdx = int(sys.argv[1]) if len(sys.argv)>1 else 0
    with sqlite3.connect('asus.sqlite3') as conn:
        csr=conn.cursor()
        rows=csr.execute("SELECT id, file_url, file_sha1"
                " FROM TFiles ORDER BY id LIMIT -1 OFFSET %d"%startIdx).fetchall()
        for idx, row in enumerate(rows,startIdx):
            devId, url,fileSha1=row
            if fileSha1 or not url:
                continue
            uprint('idx=%s, url=%s'%(idx,url))
            url = safeUrl(url)
            uprint('url='+url)
            fname=urlFileName(url)
            uprint('download "%s"'%(fname))
            fname = path.join(dlDir, fname)
            try:
                downloadFile(url, fname)
            except urllib.error.HTTPError as ex:
                print(ex)
                continue
            except OSError as ex:
                if ex.errno == 28:
                    print(ex);print('[Errno 28] No space left on device')
                    break
            except Exception as ex:
                ipdb.set_trace()
                traceback.print_exc()
                continue

            fileSha1=getFileSha1(fname)
            fileSize=path.getsize(fname)
            print('sha1="%s" for "%s"'%(fileSha1,fname))
            csr.execute("UPDATE TFiles SET file_sha1=:fileSha1,"
                    " file_size=:fileSize WHERE id=:devId", locals())
            conn.commit()
            uprint('UPDATE fileSha1=%(fileSha1)s, fileSize=%(fileSize)s'
                    ' WHERE id="%(devId)s"' %locals())
            with ftputil.FTPHost(ftpHostName,ftpUserName,ftpPassword) as ftp:
                ftp.upload(fname, path.basename(fname))
                uprint('uploaded "%s" to ftp://%s/'
                    %(path.basename(fname), ftpHostName))
            os.remove(fname)

if __name__=='__main__':
    main()
