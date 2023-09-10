import os
from html import escape
import json
import urllib.parse
import requests
from colorama import Fore, Back, Style
from scripts.file_manage import extranetwork_folder

class civitaimodels:
    '''civitaimodels: Handle the response of civitai models api v1.'''
    def __init__(self, url:str, json_data:dict=None, content_type:str=None):
        self.jsonData = json_data
        self.contentType = content_type
        self.showNsfw = False
        self.baseUrl = url
        self.modelIndex = None
        self.versionIndex = None
        self.modelVersionInfo = None
        self.requestError = None
        self.saveFolder = None
    def updateJsonData(self, json_data:dict=None, content_type:str=None):
        '''Update json data.'''
        self.jsonData = json_data
        self.contentType = self.contentType if content_type is None else content_type
        self.showNsfw = False
        self.modelIndex = None
        self.versionIndex = None
        self.modelVersionInfo = None
        self.requestError = None
        self.saveFolder = None
    def setBaseUrl(self,url:str):
           self.url = url
    def getBaseUrl(self) -> str:
            return self.baseUrl
    def getJsonData(self) -> dict:
        return self.jsonData

    def setShowNsfw(self, showNsfw:bool):
        self.showNsfw = showNsfw
    def isShowNsfw(self) -> bool:
        return self.showNsfw
    def setContentType(self, content_type:str):
        self.contentType = content_type
    def getContentType(self) -> str:
        return self.contentType
    def getRequestError(self) -> requests.exceptions.RequestException:
        return self.requestError
    def setSaveFolder(self, path):
        self.saveFolder = path
    def getSaveFolder(self):
        return self.saveFolder

    # Models
    def getModelNames(self) -> dict: #include nsfw models
        model_dict = {}
        for item in self.jsonData['items']:
            model_dict[item['name']] = item['name']
        return model_dict
    def getModelNamesSfw(self) -> dict: #sfw models
        '''Return SFW items names.'''
        model_dict = {}
        for item in self.jsonData['items']:
            if not item['nsfw']:
                model_dict[item['name']] = item['name']
        return model_dict   
        
    # Model
    def getModelNameByID(self, id:int) -> str:
        name = None
        for item in self.jsonData['items']:
            if int(item['id']) == int(id):
                name = item['name']
        return name
    def getIDByModelName(self, name:str) -> str:
        id = None
        for item in self.jsonData['items']:
            if item['name'] == name:
                id = int(item['id'])
        return id
    def isNsfwModelByID(self, id:int) -> bool:
        nsfw = None
        for item in self.jsonData['items']:
            if int(item['id']) == int(id):
                nsfw = item['nsfw']
        return nsfw
    def selectModelByIndex(self, index:int):
        if index >= 0 and index < len(self.jsonData['items']):
            self.modelIndex = index
        return self.modelIndex
    def selectModelByID(self, id:int):
        for index, item in enumerate(self.jsonData['items']):
            if int(item['id']) == int(id):
                self.modelIndex = index
        return self.modelIndex
    def selectModelByName(self, name:str) -> int:
        if name is not None:
            for index, item in enumerate(self.jsonData['items']):
                if item['name'] == name:
                    self.modelIndex = index
            #print(f'{name} - {self.modelIndex}')
        return self.modelIndex
    def isNsfwModel(self) -> bool:
        return self.jsonData['items'][self.modelIndex]['nsfw']
    def getIndexByModelName(self, name:str) -> int:
        retIndex = None
        if name is not None:
            for index, item in enumerate(self.jsonData['items']):
                if item['name'] == name:
                    retIndex = index
        return retIndex
    def getSelectedModelIndex(self) -> int:
        return self.modelIndex
    def getSelectedModelName(self) -> str:
        item = self.jsonData['items'][self.modelIndex]
        return item['name']
    def getSelectedModelID(self) -> str:
        item = self.jsonData['items'][self.modelIndex]
        return int(item['id'])
    def allows2permissions(self) -> dict:
        '''Convert allows to permissions. Select model first.
            [->Reference](https://github.com/civitai/civitai/blob/main/src/components/PermissionIndicator/PermissionIndicator.tsx#L15)'''
        permissions = {}
        if self.modelIndex is None:
            print(Fore.LIGHTYELLOW_EX + 'Select item first.' + Style.RESET_ALL )
        else:
            if self.modelIndex is not None:
                item = self.jsonData['items'][self.modelIndex]
                allowNoCredit = item['allowNoCredit']
                allowCommercialUse = item['allowCommercialUse']
                allowDerivatives = item['allowDerivatives']
                allowDifferentLicense = item['allowDifferentLicense']
                canSellImages = allowCommercialUse == 'Image' or allowCommercialUse == 'Rent' or allowCommercialUse == 'RentCivit' or allowCommercialUse == 'Sell'
                canRentCivit = allowCommercialUse == 'Rent' or allowCommercialUse == 'RentCivit' or allowCommercialUse == 'Sell'
                canRent = allowCommercialUse == 'Rent' or allowCommercialUse == 'Sell'
                canSell = allowCommercialUse == 'Sell'
                permissions['allowNoCredit'] = allowNoCredit
                permissions['canSellImages'] = canSellImages
                permissions['canRentCivit'] = canRentCivit
                permissions['canRent'] = canRent
                permissions['canSell'] = canSell
                permissions['allowDerivatives'] = allowDerivatives
                permissions['allowDifferentLicense'] = allowDifferentLicense
        return permissions
    def getModelVersionsList(self):
        '''Return modelVersions list. Select item before.'''
        versionNames = {}
        if self.modelIndex is None:
            print(Fore.LIGHTYELLOW_EX + 'Select item first.' + Style.RESET_ALL )
        else:
            item = self.jsonData['items'][self.modelIndex]
            for version in item['modelVersions']:
                versionNames[version['name']] = version["name"]
        return versionNames

    # Version
    def selectVersionByID(self, ID:int) -> int:
        item = self.jsonData['items'][self.modelIndex]
        for index, model in enumerate(item['modelVersions']):
            if int(model['id']) == int(ID):
                    self.versionIndex = index
        return self.versionIndex
    def selectVersionByName(self, name:str) -> int:
        '''Select model version by name. Select model first.
        
        Args:
            ID (int): version ID
        Returns:
            int: index number of the version
        '''
        if name is not None:
            item = self.jsonData['items'][self.modelIndex]
            for index, model in enumerate(item['modelVersions']):
                if model['name'] == name:
                        self.versionIndex = index
        return self.versionIndex
    def getSelectedVersionName(self):
        return self.jsonData['items'][self.modelIndex]['modelVersions'][self.versionIndex]['name']
    def getSelectedVersionBaeModel(self):
        #print(f"{self.jsonData['items'][self.modelIndex]['modelVersions']}")
        return self.jsonData['items'][self.modelIndex]['modelVersions'][self.versionIndex]['baseModel']
    def setModelVersionInfo(self, modelInfo:str):
        self.modelVersionInfo = modelInfo
    def getModelVersionInfo(self) -> str:
        return self.modelVersionInfo
    def getVersionDict(self) -> dict:
        version_dict = {}
        item = self.jsonData['items'][self.modelIndex]
        version_dict = item['modelVersions'][self.versionIndex]
        return version_dict

    def makeModelInfo2(self, versionName:str) -> dict:
        '''not yet'''
        modelInfo = {}
        if self.modelIndex is None:
            print(Fore.LIGHTYELLOW_EX + f'Select item first. {self.modelID}' + Style.RESET_ALL )
        else:
            for index, item in enumerate(self.jsonData['items']):
                if int(item['id']) == self.modelID:
                    modelInfo = self.jsonData['items'][index]
                for version in item['modelVersions']:
                    if version['name'] == versionName:
                        modelInfo['modelVersion'] = version
        return modelInfo
    def makeModelInfo(self) -> dict:
        modelInfo = {
            'description':"",
            'trainedWords':"",
            'files':{},
            'allow':{},
        }
        item = self.jsonData['items'][self.modelIndex]
        version = item['modelVersions'][self.versionIndex]
        modelInfo['id'] = item['id']
        modelInfo['model_name'] = item['name']
        modelInfo['type'] = item['type']
        modelInfo['nsfw'] = item['nsfw']
        modelInfo['creator'] = item['creator']['username']
        modelInfo['tags'] = item['tags']
        modelInfo['description'] = item['description']
        modelInfo['allow']['allowNoCredit'] = item['allowNoCredit']
        modelInfo['allow']['allowCommercialUse'] = item['allowCommercialUse']
        modelInfo['allow']['allowDerivatives'] = item['allowDerivatives']
        modelInfo['allow']['allowDifferentLicense'] = item['allowDifferentLicense']
        modelInfo['version_name'] = version['name']
        modelInfo['modelId'] = version['modelId']
        modelInfo['trainedWords'] = ", ".join(version['trainedWords'])
        modelInfo['baseModel'] = version['baseModel']
        modelInfo['versionDescription'] = version['description']
        for file in version['files']:
            modelInfo['files'][file['name']] = file['downloadUrl']
        pics = []
        for pic in version['images']:
            pics.append({ 'id' : pic['id'],
                            'nsfw' : pic['nsfw'],
                            'url': pic["url"],
                            'meta' : pic['meta'],
                            'type' : pic['type'],
                            })
        modelInfo['images'] = pics
        modelInfo['downloadUrl'] = version['downloadUrl'] if 'downloadUrl' in version else None
        modelInfo['html'] = self.modelInfoHtml(modelInfo)
        self.setModelVersionInfo(modelInfo)
        return modelInfo

    def getUrlByName(self, model_filename=None):
        if self.modelIndex is None:
            #print(Fore.LIGHTYELLOW_EX + f'getUrlByName: Select model first. {model_filename}' + Style.RESET_ALL )
            return
        if self.versionIndex is None:
            #print(Fore.LIGHTYELLOW_EX + f'getUrlByName: Select version first. {model_filename}' + Style.RESET_ALL )
            return
        #print(Fore.LIGHTYELLOW_EX + f'File name . {model_filename}' + Style.RESET_ALL )
        item = self.jsonData['items'][self.modelIndex]
        version = item['modelVersions'][self.versionIndex]
        dl_url = None
        for file in version['files']:
            if file['name'] == model_filename:
                dl_url = file['downloadUrl']
        return dl_url

    # Pages
    def getCurrentPage(self) -> str:
        return f"{self.jsonData['metadata']['currentPage']}"
    def getTotalPages(self) -> str:
        return f"{self.jsonData['metadata']['totalPages']}"
    def getPages(self) -> str:
        return f"{self.getCurrentPage()}/{self.getTotalPages()}"
    def nextPage(self) -> str:
        return self.jsonData['metadata']['nextPage'] if 'nextPage' in self.jsonData['metadata'] else None
    def prevPage(self) -> str:
        return self.jsonData['metadata']['prevPage'] if 'prevPage' in self.jsonData['metadata'] else None

    # HTML
    # Make model cards html
    def modelCardsHtml(self, model_names, jsID=0):
        '''Generate HTML of model cards.'''
        HTML = '<div class="column civmodellist">'
        for index, item in enumerate(self.jsonData['items'], ):
            for k,model in model_names.items():
                if model_names[k] == item['name']:
                    #print(f'Item:{item["modelVersions"][0]["images"]}')
                    model_name = escape(item["name"].replace("'","\\'"),quote=True)
                    #print(f'{model_name}')
                    #print(f'Length: {len(item["modelVersions"][0]["images"])}')
                    nsfw = ""
                    alreadyhave = ""
                    ID = item['id']
                    imgtag = f'<img src="./file=html/card-no-preview.png"/>'
                    if any(item['modelVersions']):
                        if len(item['modelVersions'][0]['images']) > 0:
                            for img in item['modelVersions'][0]['images']:
                                #print(f'{img["type"]}')
                                if img['type'] == "image":
                                    if img['nsfw'] != "None" and not self.isShowNsfw():
                                        nsfw = 'civcardnsfw'
                                    imgtag = f'<img src={img["url"]}></img>'
                                    break
                                elif img['type'] == 'video':
                                    if img['nsfw'] != "None" and not self.isShowNsfw():
                                        nsfw = 'civcardnsfw'
                                    imgtag = f'<video loop autoplay muted poster={img["url"]}>'
                                    imgtag += f'<source  src={img["url"]} type="video/webm"/>'
                                    imgtag += f'<source  src={img["url"]} type="video/mp4"/>'
                                    imgtag += f'<img src={img["url"]} type="image/gif"/>'
                                    imgtag += f'</video>'
                                    break
                        for file in item['modelVersions'][0]['files']:
                            file_name = file['name']
                            base_model = item["modelVersions"][0]['baseModel']
                            folder = extranetwork_folder(self.getContentType(),item["name"],base_model, item['nsfw'])
                            path_file = os.path.join(folder, file_name)
                            #print(f"{path_file}")
                            if os.path.exists(path_file):
                                alreadyhave = "civmodelcardalreadyhave"
                                break
                    HTML = HTML +  f'<figure class="civmodelcard {nsfw} {alreadyhave}" onclick="select_model(\'Index{jsID}:{index}:{ID}\')">'\
                                    +  imgtag \
                                    +  f'<figcaption>{item["name"]}</figcaption></figure>'
        HTML = HTML + '</div>'
        return HTML

    def meta2html(self, meta:dict) -> str:
        #convert key name as infotext
        renameKey = {
            'prompt':'Prompt',
            'negativePrompt': 'Negative prompt',
            'steps': 'Steps',
            'seed': 'Seed',
            'sampler': 'Sampler',
            'cfgScale': 'CFG scale',
            'clipSkip': 'Clip skip'
                }
        infotext = {renameKey.get(key, key): value for key, value in meta.items()}
        html = ""
        if 'Prompt' in infotext:
            html += f'{escape(str(infotext["Prompt"]))}<br/>'
            del infotext["Prompt"]
        if 'Negative prompt' in infotext:
            html += f'<var style="font-weight:bold;">{escape(str("Negative prompt"))}</var>: {escape(str(infotext["Negative prompt"]))}<br/><br/>'
            del infotext["Negative prompt"]
        for key, value in infotext.items():
            html += f'<var style="font-weight:bold;">{escape(str(key))}</var>: {escape(str(value))}, '
        return html.rstrip(', ')

    def modelInfoHtml(self, modelInfo:dict) -> str:
        '''Generate HTML of model info'''
        img_html = '<div class="sampleimgs">'
        for pic in modelInfo['images']:
            nsfw = ""
            imgStyle = 'style="width:20em;"'
            if pic['meta']:
                infotext = self.meta2html(pic['meta'])
                imgStyle ='style="width:20em;cursor:copy;" onclick="copyInnerText(this);"'
            if pic['nsfw'] != "None" and not self.showNsfw:
                nsfw = 'class="civnsfw"'
            img_html +=  f'<div {nsfw} style="display:flex;align-items:flex-start;gap:1em;">'
            if pic['type'] == 'image':
                img_html += f'<img src={pic["url"]}  {imgStyle}/>'
            else:
                img_html += f'<video loop autoplay muted poster={pic["url"]} {imgStyle}>'
                img_html += f'<source  src={pic["url"]} type="video/webm"/>'
                img_html += f'<source  src={pic["url"]} type="video/mp4"/>'
                img_html += f'<img src={pic["url"]} type="image/gif"/>'
                img_html += f'</video>'
            if pic['meta']:
                img_html += f'<div style="text-align:left;line-height: 1.5em;">'
                img_html += infotext
                img_html += '</div>'
            img_html += '</div></br>'
        img_html += '</div>'
        #function:copy to clipboard
        output_html = '<script>'\
            'function copyInnerText(node) {'\
            'if (node.nextSibling != null) {'\
            'return navigator.clipboard.writeText(node.nextSibling.innerText).then('\
			'function () {'\
				'alert("Copied infotext");'\
			'}).catch('\
			    'function (error) {'\
				'alert((error && error.message) || "Failed to copy infotext");'\
			'})} }'\
            '</script>'
        if modelInfo['nsfw']:
            output_html += '<h1>NSFW</b></h1>'
        output_html += f'<h1>Model: {escape(str(modelInfo["model_name"]))}</h1>'\

        output_html += f'<div style="">'
        output_html += '<div style="float:right;width:35%;margin:-16px 0 1em 1em;">'\
                        '<h2>Permissions</h2>'\
            f'{self.permissionsHtml(self.allows2permissions())}'\
            f'<p>{escape(str(modelInfo["allow"]))}</p></div>'
        output_html += '</div>'
        output_html += f'<div style="overflow-wrap: anywhere;">'\
            f'<div><b>Civitai link</b> (if exist): '\
            f'<a href="https://civitai.com/models/{escape(str(modelInfo["id"]))}" target="_blank">'\
            f'https://civitai.com/models/{str(modelInfo["id"])}</a><br/>'\
            f'<b>Version</b>: {escape(str(modelInfo["version_name"]))}<br/>'\
            f'<b>Uploaded by</b>: {escape(str(modelInfo["creator"]))}<br/>'\
            f'<b>Base Model</b>: {escape(str(modelInfo["baseModel"]))}<br/>'\
            f'<b>Tags</b>: {escape(str(modelInfo["tags"]))}<br/>'\
            f'<b>Trained Tags</b>: {escape(str(modelInfo["trainedWords"]))}<br/>'\
            f'<a href={modelInfo["downloadUrl"]}>'\
            '<b>Download Here</b></a></div>'
        output_html += '<div><h2>Model description</h2>'\
            f'<p>{modelInfo["description"]}</p></div>'

        if modelInfo["versionDescription"]:
            output_html += f'<div><h2>Version description</h2>'\
            f'<p>{modelInfo["versionDescription"]}</p></div>'
        output_html += '</div>'

        output_html += f'<div style="clear:both;"><h2>Images</h3>'\
                        f'<p>Click image to copy infotext</p>'\
                        f'{img_html}</div>'
        return output_html
    
    def permissionsHtml(self, premissions:dict, msgType:int=3) -> str:
        chrCheck = '✅'
        chrCross = '❌'
        html1 = '<div>'\
                '<p>This model permits users to:</br>'\
                f'{chrCheck if premissions["allowNoCredit"] else chrCross} : Use the model without crediting the creator<br/>'\
                f'{chrCheck if premissions["canSellImages"] else chrCross} : Sell images they generate<br/>'\
                f'{chrCheck if premissions["canRent"] else chrCross} : Run on services that generate images for money<br/>'\
                f'{chrCheck if premissions["canRentCivit"] else chrCross} : Run on Civitai<br/>'\
                f'{chrCheck if premissions["allowDerivatives"] else chrCross} : Share merges using this model<br/>'\
                f'{chrCheck if premissions["canSell"] else chrCross} : Sell this model or merges using this model<br/>'\
                f'{chrCheck if premissions["allowDifferentLicense"] else chrCross} : Have different permissions when sharing merges</p>'\
                '</p></div>'
        html2 = '<div>'\
                '<p><span style=color:crimson>'
        html2 += 'Creator credit required</br>' if not premissions["allowNoCredit"] else ''
        html2 += 'No selling images</br>' if not premissions["canSellImages"] else ''
        html2 += 'No Civitai generation</br>' if not premissions["canRentCivit"] else ''
        html2 += 'No generation services</br>' if not premissions["canRent"] else ''
        html2 += 'No selling models</br>' if not premissions["canSell"] else ''
        html2 += 'No sharing merges</br>' if not premissions["allowDerivatives"] else ''
        html2 += 'Same permissions required' if not premissions["allowDifferentLicense"] else ''
        html2 += '</span></p></div>'

        html = f'<p><strong>Check the source license yourself.</strong></p>'
        if msgType == 1:
            html += html1
        elif msgType == 2:
            html += html2
        else:
            html += html2 + html1
        return html

    #REST API
    def makeRequestQuery(self, content_type, sort_type, period, use_search_term, search_term=None):
        query = {'types': content_type, 'sort': sort_type}
        if not period == "AllTime":
            query |= {'period': period}
        if use_search_term != "No" and search_term:
            #search_term = search_term.replace(" ","%20")
            if use_search_term == "User name":
                query |= {'username': search_term }
            elif use_search_term == "Tag":
                query |= {'tag': search_term }
            else:
                query |= {'query': search_term }
        return query

    def updateQuery(self, url:str , addQuery:dict) -> str:
        parse = urllib.parse.urlparse(url)
        strQuery = parse.query
        dictQuery = urllib.parse.parse_qs(strQuery)
        query = dictQuery | addQuery
        newURL = parse._replace(query=urllib.parse.urlencode(query,  doseq=True, quote_via=urllib.parse.quote))
        return urllib.parse.urlunparse(newURL)

    def requestApi(self, url=None, query=None):
        self.requestError = None
        if url is None:
            url = self.getBaseUrl()
        if query is not None:
            query = urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
        # Make a GET request to the API
        try:
            response = requests.get( url, params=query, timeout=(10,15))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(Fore.LIGHTYELLOW_EX + "Request error: " , e)
            print(Style.RESET_ALL)
            #print(f"Query: {payload} URL: {response.url}")
            data = self.jsonData # No update data
            self.requestError = e
        else:
            response.encoding  = "utf-8" # response.apparent_encoding
            data = json.loads(response.text)
        # Check the status code of the response
        #if response.status_code != 200:
        #  print("Request failed with status code: {}".format(response.status_code))
        #  exit()            
        return data
    