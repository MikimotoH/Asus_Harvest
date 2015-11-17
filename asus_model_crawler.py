#!/usr/bin/env python3
# coding: utf-8
import harvest_utils
from harvest_utils import waitVisible, waitText, getElems, getFirefox,driver,waitTextChanged, getElemText, isReadyState, waitUntil
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement
import sys
import sqlite3
import re
import time
import datetime
from datetime import datetime
import ipdb
import traceback
from my_utils import uprint,ulog,getFuncName
from contextlib import suppress
import random
import math
import html2text
from belkin_art_parse import getSizeDateVersion
from urllib import parse


driver,conn=None,None
category,productName,model='','',''
prevTrail=[]
startTrail=[]

def getScriptName():
    from os import path
    return path.splitext(path.basename(__file__))[0]

def getStartIdx():
    global startTrail
    if startTrail:
        return startTrail.pop(0)
    else:
        return 0

def sql(query:str, var=None):
    global conn
    csr=conn.cursor()
    try:
        if var:
            rows = csr.execute(query,var)
        else:
            rows = csr.execute(query)
        if not query.startswith('SELECT'):
            conn.commit()
        if query.startswith('SELECT'):
            return rows.fetchall()
        else:
            return
    except sqlite3.Error as ex:
        print(ex)
        raise ex

def glocals()->dict:
    """ globals() + locals()
    """
    import inspect
    ret = dict(inspect.stack()[1][0].f_locals)
    ret.update(globals())
    return ret

def retryUntilTrue(statement, timeOut:float=6.2, pollFreq:float=0.3):
    timeElap=0
    while timeElap<timeOut:
        timeBegin=time.time()
        try:
            r = statement()
            ulog('r="%s"'%str(r))
            if r is not None:
                return r
        except (StaleElementReferenceException, StopIteration):
            pass
        except Exception as ex:
            ulog('raise %s %s'%(type(ex),str(ex)))
            raise ex
        ulog('sleep %f secs'%pollFreq)
        time.sleep(pollFreq)
        timeElap+=(time.time()-timeBegin)
    raise TimeoutException(getFuncName()+': timeOut=%f'%timeOut)


def osWalker():
    try:
        oss = getElems('#div_os dl a')
        startIdx=getStartIdx()
        numOss=len(oss)
        for idx in range(startIdx, numOss):
            osTxt = oss[idx].text
            if osTxt != 'Others':
                continue
            ulog('click %s,"%s"'%(idx, osTxt))
            prevTrail+=[idx]
            oss[idx].click()
            waitClickable('#a_start').click()
            fileWalker()
            prevTrail.pop()
            oss = getElems('#div_os dl a')
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')


def modelWalker():
    try:
        models = getElems('#dl_models a')
        startIdx=getStartIdx()
        numModels=len(models)
        for idx in range(startIdx, numModels):
            modelTxt = models[idx].text
            ulog('click %s,"%s"'%(idx, modelTxt))
            prevTrail+=[idx]
            models[idx].click()
            osWalker()
            prevTrail.pop()
            models = getElems('#dl_models a')
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')

    
def seriesWalker():
    keywords=['Router', 'NAS', 'Range Extender', 'IP Camera',
            'Internet Camera', 'LAN Switch', 'PowerLine', 'VPN/Firewall' ]
    try:
        series = getElems('#dl_series a')
        startIdx=getStartIdx()
        numSeries=len(series)
        for idx in range(startIdx, numSeries):
            seriesTxt = series[idx].text
            if not (seriesTxt /inin/ keywords):
                continue
            ulog('idx=%s, click "%s"'%(idx,seriesTxt))
            prevTrail+=[idx]
            series[idx].click()
            modelWalker()
            prevTrail.pop()
            series = getElems('#dl_series a')
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')

def goToUrl(url:str):
    global driver
    ulog('%s'%url)
    driver.get(url)
    waitUntil(isReadyState)

productTxt=''
def productWalker():
    keywords=['Wireless', 'Networking']
    global driver, prevTrail, productTxt
    rootUrl='http://support.asus.com/Select/ModelSelect.aspx?SLanguage=en&type=1&KeepThis=true&#'
    try:
        goToUrl(rootUrl)
        products = getElems('.Action_06 a')
        numProducts = len(products)
        startIdx=getStartIdx()
        for idx in range(startIdx, numProducts):
            productTxt = products[idx].text
            if productTxt not in keywords:
                continue
            ulog('click %s "%s"'%(idx,productTxt))
            prevTrail+=[idx]
            seriesWalker()
            prevTrail.pop()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')

def main():
    global startTrail, prevTrail,driver,conn
    try:
        startTrail = [int(re.search(r'\d+', _).group(0)) for _ in sys.argv[1:]]
        ulog('startTrail=%s'%startTrail)
        conn=sqlite3.connect('asus.sqlite3')
        sql("CREATE TABLE IF NOT EXISTS TFiles("
            "id INTEGER NOT NULL,"
            "product TEXT," # Wireless, Networking
            "series TEXT," #  "AP/Router"
            "model TEXT," # F9K1104
            "rel_date DATE," # Post Date: 06/20/2012 
            "fw_ver TEXT," # Download version: 1.00.23 
            "file_size INTEGER," # Size: 3.74 MB
            "fw_desc TEXT,"
            "page_url TEXT," # http://belkin.force.com/Articles/articles/en_US/Download/7371
            "file_url TEXT," # http://nextnet.belkin.com/update/files/F9K1104/v1/WW/F9K1104_WW_1.0.23.bin
            "on_click TEXT,"
            "tree_trail TEXT," # [26, 2, 1, 0, 0]
            "file_sha1 TEXT," # 5d3bc16eec2f6c34a5e46790b513093c28d8924a
            "PRIMARY KEY (id)"
            "UNIQUE(model,fw_ver)"
            ")")
        driver=harvest_utils.getFirefox()
        harvest_utils.driver=driver
        prevTrail=[]
        productWalker()
        driver.quit()
        conn.close()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        driver.save_screenshot(getScriptName()+'_'+getFuncName()+'_excep.png')

if __name__=='__main__':
    try:
        main()
    except Exception as ex:
        ipdb.set_trace()
        traceback.print_exc()
        try:
            driver.save_screenshot(getScriptName()+'_excep.png')
            driver.quit()
        except Exception:
            pass

