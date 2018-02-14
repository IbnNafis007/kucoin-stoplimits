# For managing HTTP
import requests
import time

# Time offset for KuCoin, because the server isn't well-synced for some reason
timeOffset = -8

# Make request
retryDelay = 3
def request(method, url, headers, parent):
    global timeOffset
    req = requests.request(method, url, headers=headers)

    while req.status_code >= 300:
        if req.status_code == 401 and req.json()['msg'] == 'Invalid nonce':
            global timeOffset
            sentTime = headers['KC-API-NONCE']
            recvTime = req.json()['timestamp']
            timeDiff = recvTime - float(sentTime)
            timeOffset += (timeDiff/1000)

        else:
            print 'Exception: Caught an error. Status code was: %s for action %s. Gonna retry.' % (req.status_code, parent.__class__.__name__)
            time.sleep(retryDelay)

        return parent.call() # TODO: Could this be an issue if it calls the child?

    try:
        req.json()
    except Exception:
        print 'Error in request for some reason?'
        print 'Code: %s' % req.status_code
        print 'Headers: %s' % req.headers
        print 'Text: %s' % req.text
        raise Exception('Debug')

    # API errors throw out and inform the user for debugging
    if not req.json()['success']:
        message = req.json()['msg']
        errorInfo = (parent.__class__.__name__, message)
        raise Exception('Request failure calling %s.\n\nError: %s' % errorInfo)

    return req.json()['data']