from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
from time import sleep
from urllib import parse
from selenium.common.exceptions import NoSuchElementException, \
        TimeoutException, StaleElementReferenceException, \
        WebDriverException
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from my_utils import uprint,ulog
from contextlib import contextmanager


def getFirefox(dontShowImage=True, downloadDir='/tmp', unstable=False):
    """get Firefox Webdriver object
    """
    proxy = Proxy(dict(proxyType=ProxyType.AUTODETECT))
    profile = webdriver.FirefoxProfile()
    profile.set_preference("plugin.state.flash", 0)
    profile.set_preference("plugin.state.java", 0)
    profile.set_preference("media.autoplay.enabled", False)
    # 2=dont_show, 1=normal
    showImage= 2 if dontShowImage else 1
    profile.set_preference("permissions.default.image", showImage)
    if unstable:
        profile.set_preference("webdriver.load.strategy", "unstable")
    else:
        # profile.set_preference("webdriver.load.strategy", "fast")
        pass
    # automatic download
    # 2 indicates a custom (see: browser.download.dir) folder.
    profile.set_preference("browser.download.folderList", 2)
    # whether or not to show the Downloads window when a download begins.
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", downloadDir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 
        "application/octet-stream"+\
        ",application/zip"+\
        ",application/x-rar-compressed"+\
        ",application/x-gzip"+\
        ",application/msword")
    return webdriver.Firefox(firefox_profile=profile, proxy=proxy)


def safeFileName(s:str) -> str:
    return parse.quote(s, ' ()[],')


driver=None

def waitElem(css:str, timeOut:float=30, pollFreq:float=2)->WebElement:
    global driver
    wait = WebDriverWait(driver, timeOut, poll_frequency=pollFreq)
    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,css)))

def hasElem(css:str,timeOut:float=30, pollFreq:float=2) -> bool:
    try:
        waitElem(css,timeOut,pollFreq)
        return True
    except TimeoutException:
        return False

def mouseClick(css:str):
    global driver
    actions = ActionChains(driver)
    el = waitElem(css)
    actions.move_to_element(el).click(el).perform()

def mouseOver(css:str):
    global driver
    actions = ActionChains(driver)
    el = waitElem(css)
    actions.move_to_element(el).perform()


def waitVisible(css:str, timeOut:float=30, pollFreq:float=2.0) -> WebElement :
    global driver
    wait = WebDriverWait(driver, timeOut, poll_frequency=pollFreq)
    return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,css)))

def getElems(css:str, timeOut:float=30, pollFreq:float=2.0) -> [WebElement]:
    global driver
    waitVisible(css,timeOut,pollFreq)
    return driver.find_elements_by_css_selector(css)


def getText(css:str, timeOut:float=60, interval:float=3)->str:
    global driver
    timeElapsed=0.0
    while timeElapsed < timeOut:
        beginTime=time.time()
        try:
            return driver.execute_script("return "
                "document.querySelector('%s').textContent"%css)
        except WebDriverException as ex:
            time.sleep(interval)
            timeElapsed+=(time.time()- beginTime)
    raise TimeoutException('[getText] TimeOut css='+css)

def getNumElem(css:str):
    global driver
    return driver.execute_script("return "
        "document.querySelectorAll('%s').length"%css)

def getElemText(elem:WebElement, timeOut:float=60, pollFreq:float=3.0) -> str:
    timeElapsed=0.0
    while timeElapsed < timeOut:
        beginTime=time.time()
        try:
            return elem.text.strip()
        except StaleElementReferenceException:
            pass
        time.sleep(pollFreq)
        timeElapsed+=(time.time()- beginTime)
    raise TimeoutException('[getElemText] Time out elem='+str(elem))

def clickElem(elem:WebElement, timeOut:float=29, pollFreq:float=0.7):
    timeElapsed=0.0
    while timeElapsed < timeOut:
        beginTime=time.time()
        try:
            elem.click()
            return
        except StaleElementReferenceException:
            pass
        time.sleep(pollFreq)
        timeElapsed+=(time.time()- beginTime)
    raise TimeoutException('[getElemText] Time out elem='+str(elem))

def getElemAttr(elem:WebElement, attr:str, timeOut:float=30, pollFreq:float=1) -> str:
    timeElapsed=0.0
    while timeElapsed < timeOut:
        beginTime=time.time()
        try:
            return elem.get_attribute(attr)
        except StaleElementReferenceException:
            pass
        time.sleep(pollFreq)
        timeElapsed+=(time.time()- beginTime)
    raise TimeoutException('[getElemAttr] Time out elem='+str(elem))


def waitText(css:str, timeOut:float=30, pollFreq:float=2) -> str :
    timeElapsed=0.0
    while timeElapsed < timeOut:
        beginTime = time.time()
        try:
            return waitVisible(css, pollFreq, pollFreq/2).text
        except (TimeoutException, StaleElementReferenceException):
            pass
        time.sleep(pollFreq)
        timeElapsed += (time.time()-beginTime)
    raise TimeoutException('[waitText] Time Out css='+css)

def waitTextA(css:str, timeOut:float=30, pollFreq:float=2) -> str :
    global driver
    timeElapsed=0.0
    while timeElapsed < timeOut:
        beginTime = time.time()
        try:
            return driver.find_element_by_css_selector(css).text
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
            pass
        time.sleep(pollFreq)
        timeElapsed += (time.time()-beginTime)
    return None

def waitClickable(css:str, timeOut:float=60,pollFreq:float=2.0) -> WebElement :
    global driver
    wait = WebDriverWait(driver, timeOut, poll_frequency=pollFreq)
    return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,css)))

def waitTextChanged(css:str,oldText:str=None) -> str:
    if oldText is None:
        oldText=getText(css)
    for x in range(20):
        newText = getText(css)
        if newText != oldText:
            return newText
        sleep(3)
    raise TimeoutException('[waitTextChanged] oldText="%s", '
            'newText="%s"'%(oldText,newText))

def waitUntilStable(css:str, timeOut:float=5, pollFreq:float=0.5):
    oldText = waitText(css)
    # uprint('waitUntilStable: oldText="%s"'%oldText)
    timeElapsed=0.0
    while timeElapsed<timeOut:
        beginTime=time.time()
        newText=waitText(css)
        if newText != oldText:
            # uprint('waitUntilStable: newText="%s"'%newText)
            oldText=newText
            timeElpased=0
        else:
            time.sleep(pollFreq)
            timeElapsed += time.time()-beginTime

def dumpSnapshot(msg:str):
    global driver
    fileTitle = safeFileName(msg) 
    driver.save_screenshot(fileTitle+'.png')
    with open(fileTitle+'.html', 'w', encoding='utf-8-sig') as fout:
        fout.write(driver.page_source)

def waitUntil(cond, timeOut:float=40, pollFreq:float=0.5):
    timeElapsed=0.0
    while timeElapsed < timeOut:
        timeBegin=time.time()
        if cond()==True:
            return True
        time.sleep(pollFreq)
        timeElapsed += (time.time()-timeBegin)
    print("waitUntil: Timeout cond()=%s"%(str(cond)))
    return False

def waitUntilA(expr, timeOut:float=40, pollFreq:float=0.5):
    timeElapsed=0.0
    while timeElapsed < timeOut:
        timeBegin=time.time()
        try:
            res= expr()
            if res is not None:
                return res
        except Exception:
            pass
        time.sleep(pollFreq)
        timeElapsed += (time.time()-timeBegin)
    print("waitUntilA: Timeout expr=%s"%(str(expr)))
    return None

def isReadyState()->bool:
    # AFAICT Selenium offers no better way to wait for the document to be loaded,
    # if one is in ignorance of its contents.
    global driver
    return driver.execute_script("return document.readyState") == "complete"

def mouseClickE(e:WebElement, timeOut=7,pollFreq=0.3):
    global driver
    timeElap=0
    while timeElap<timeOut:
        timeBegin=time.time()
        try:
            actions = ActionChains(driver)
            actions.move_to_element(e).click(e).perform()
            return
        except StaleElementReferenceException:
            time.sleep(pollFreq)
            timeElap += (time.time()-timeBegin)
            continue

@contextmanager
def UntilTextChanged(css:str, timeOut:float=30, pollFreq:float=2,noWait=False)->str:
    oldText = waitText(css, timeOut/4.0)
    yield
    if noWait:
        return oldText
    timeElapsed=0.0
    while timeElapsed<timeOut:
        beginTime=time.time()
        txt = waitText(css, timeOut)
        if txt != oldText:
            return txt
        time.sleep(pollFreq)
        timeElapsed += time.time()-beginTime
    raise TimeoutException('[UntilTextChanged] timeOut for css='+css)

def mouseOver(elm,xoffset=0,yoffset=0):
    global driver
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(elm, xoffset, yoffset).perform()

def elemWithText(css:str, txt:str)->WebElement:
    global driver
    return next((_ for _ in driver.find_elements_by_css_selector(css) 
        if txt.lower() in getElemText(_).lower()), None)

def retryStable(cond, timeOut:float=5, pollFreq:float=0.5):
    oldCond = cond()
    ulog('oldCond=%s'%oldCond)
    timeElapsed=0.0
    while timeElapsed<timeOut:
        beginTime=time.time()
        newCond=cond()
        if newCond != oldCond:
            ulog('newCond=%s'%newCond)
            oldCond=newCond
            timeElpased=0
        else:
            time.sleep(pollFreq)
            timeElapsed += time.time()-beginTime
