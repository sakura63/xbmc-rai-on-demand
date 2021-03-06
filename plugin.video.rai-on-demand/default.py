'''
Created on Nov 23, 2012

@author: flavio
'''

import urllib,urllib2,sys,request,xbmcWrapper,json,cache,xbmc,xbmcgui

pluginId = int(sys.argv[1])

#addon id - name of addon directory
_id='plugin.video.rai-on-demand'
#resources directory
#_resdir = "special://home/addons/" + _id + "/resources" #add our library to python search path
#sys.path.append( _resdir + "/lib/")

def loggerMethod(top,log):
    '''use for debug'''
    print '############################## LOGGER ##############################'
    print top + '-' + log

def addLetterIndex():
    ''' This method creates the list of initial letter of all shows '''
    global pluginId,base_url
    
    letterList = request.letterIndexReq()

    # Add a list of letter
    for letter in letterList:
        xbmcWrapper.addFolder(pluginId,1,letter,{'letter': letter})
    xbmcWrapper.endOfContent(pluginId)
    
def addTvShowsByLetter(paramDict):
    ''' This methods create the list of shows starting with letter '''        
    showList = request.showsWithLetterReq(paramDict['letter'])   
    # Add the list of shows starting with the letter chosen
    for elem in showList:
        xbmcWrapper.addFolder(pluginId,2,elem.get('title'),{'title': elem.get('title'), 'image': elem.get('image'), 'linkDemand': elem.get('linkDemand')})
    xbmcWrapper.endOfContent(pluginId)    
        
def addTvShowsCategories(paramDict):
    ''' This methods create the list of shows video categories ''' 
    # LinkDemand is an URL that contains category list of the specific tv show      
    url = paramDict['linkDemand']         
    categoryList = request.showVideoCategories(url)  
    #Add the list of categories for the chosen show
    for elem in categoryList:
        xbmcWrapper.addFolder(pluginId,3,elem[1],{'title': paramDict['title'], 'categoryName': elem[1], 'contentSet-Id': elem[0], 'page': str(0)})
    xbmcWrapper.endOfContent(pluginId)  

def addTvShowsCategoryEpisodes(paramDict):
    ''' This methods create the list of video available for the previously chosen show and category '''  
    episodeList = request.showsEpisodeList(paramDict['contentSet-Id'], int(paramDict['page']))   
    # Add the list of video for the specified category
    for elem in episodeList['list']:
        video = elem.get('h264') 
        
        if video == None or len(video) < 1:
            video = elem.get('wmv')
        if video == None or len(video) < 1:
            video = elem.get('mediaUri')
        if video:
            xbmcWrapper.addVideoItemWithMode(pluginId, 5, elem.get('name'), video, 'http://www.rai.tv/'+elem.get('image'), 'http://www.rai.tv/'+str(elem.get('image_medium')))
    
    # Hanlde the next page indicator
    if int(paramDict['page'])+1 < int(episodeList['pages']):
        xbmcWrapper.addFolder(pluginId,4,'Prossima Pagina',{'title': paramDict['title'], 'contentSet-Id': paramDict['contentSet-Id'], 'page': str(int(paramDict['page'])+1)})
    
    xbmcWrapper.endOfContent(pluginId)

def getVideoUrlandPlay(paramDict):
    ''' This methods get the video url following redirect and set it to play '''
    if paramDict['videoUrl'].startswith(('http','https')):
        req = urllib2.Request(paramDict['videoUrl'])
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11')
        response = urllib2.urlopen(req)
        video = response.geturl()
    else:
        video = paramDict['videoUrl']
    
    print "VIDEO is: " + video

    videoInfo=xbmcgui.ListItem(urllib.unquote_plus(paramDict['title']), paramDict['iconImage'], paramDict['thumbnailImage'])
    videoInfo.setInfo( type="Video", infoLabels={ "Title": urllib.unquote_plus(paramDict['title']) } )
    # Play the video
    xbmc.Player().play(video, videoInfo)    

def getParams():
    ''' Utility method that returns all params passed to xbmc as a dictionary'''
    resultDict = {}
    
    if len(sys.argv) > 1 and len(sys.argv[2]) > 1:
        paramList = sys.argv[2][1:].split('&')
        for elem in paramList:
            token = elem.split('=')
            if len(token) == 2:
                resultDict[token[0]] = urllib.unquote_plus(token[1])
    
    return resultDict
        
# New plugin call
print '########################## NEW PLUGIN CALL ################################'
print "ARGUMENTS: "
print sys.argv
paramsDict=getParams()
print "PARAMS PARSED"
print paramsDict
print '############################################################################'

mode=None
try:
    mode=int(paramsDict['mode'])
except (TypeError, KeyError):
    pass
except:
    print "********* GENERIC ERROR EXCEPTION TO BE VERIFIED *********"
    print sys.exc_info()
    cache.clearFileCache()

print 'MODE - ' + str(mode)

# Mode = None - First start - List of letters
if mode == None: 
    print "Create groups"
    addLetterIndex()

# Mode = 1 - Letter chosen - List of TV shows starting with defined letter
elif mode == 1: 
    print "Create shows staring with " + paramsDict['letter']
    addTvShowsByLetter(paramsDict)

# Mode = 2 - Tv show chosen - List of video categories available    
elif mode == 2: 
    print "Create video categories for: " + paramsDict['title']
    addTvShowsCategories(paramsDict)
    
# Mode = 3 - Tv show chosen - List of episode available for that show      
elif mode == 3: 
    print "Create episode index for: " + paramsDict['title'] + ' page: ' + str(paramsDict['page'])
    addTvShowsCategoryEpisodes(paramsDict)

# Mode = 4 - Tv show chosen - List of episode available for that show for next pages    
elif mode == 4: 
    print "Create episode index for: " + paramsDict['title'] + ' page: ' + str(paramsDict['page'])
    addTvShowsCategoryEpisodes(paramsDict)

# Mode = 5 - Video chosen - Follow redirects and get the last video url   
elif mode == 5: 
    print "Get video from url: " + paramsDict['videoUrl'] + ' and play'
    getVideoUrlandPlay(paramsDict)
