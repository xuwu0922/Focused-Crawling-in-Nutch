
# encoding: utf-8
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Id$

#Evaluate Focused Crawling in Nutch in the Weapons Domain
#by Xu Wu(www.xwstudio.com)

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
import nutchpy
import json
import requests
import unicodedata

#Path to data files under segments folder
data_path = '/Users/xuwu/Documents/590DR/searchengine/nutch-sim/runtime/local/crawl_sim_new/segments/20160228232610/parse_data/part-00000/data'
text_path = '/Users/xuwu/Documents/590DR/searchengine/nutch-sim/runtime/local/crawl_sim_new/segments/20160228232610/parse_text/part-00000/data'

# We define the variables need to call the API
# Register in www.meaningCloud.com to get the key
api = 'http://api.meaningcloud.com/class-1.1'
key = ''
# url = 'https://www.gunsamerica.com/blog/weaponized-police-drones-to-hit-streets-of-north-dakota/'
model = 'IPTC_en' #IPTC_es/IPTC_en/IPTC_fr/IPTC_it/IPTC_ca/EUROVOC_es_ca/BusinessRep_es/BusinessRepShort_es

# We make the request and parse the response
def getJasonRes(url):
	parameters = {'key': key, 'model': model, 'url': url, 'src': 'sdk-python-1.1'}
	r = requests.post(api, params=parameters)
	response = r.content
	response_json = json.loads(response)
	return response_json

seq_reader = nutchpy.sequence_reader
data = seq_reader.read(data_path)
text = seq_reader.read(text_path)

urlMap = {}

text_file=open("sim2.txt", "w")
#text_file.write("Total number of urls: %d" % totUrls)

# Counters
weapon_counter=0
notfound=0
error_count=0

# IPTC codes which are related to weapons, find more details here: http://cv.iptc.org/newscodes/subjectcode
codeDict=['11001006','11016004','15051000','16012000']

for url in data:
	#url_i = url[0];
	tag = url[1]
	length=len(tag)
	parseMetaStart = tag.find("Content Metadata:")
	if parseMetaStart!=-1:
		startContentType=tag.find("Content-Type=", parseMetaStart)
		if startContentType!=-1:
			contentType = tag[startContentType+13: startContentType+18]
			if contentType=="text/":
				urlMap[url[0]]= ""

for item in text:
	url_text = item[0]

	parse_text=item[1].encode('ascii','ignore')
	parse_text=unicodedata.normalize('NFKD', item[1]).encode('ascii','ignore')
	if url_text in urlMap and len(parse_text)<=5000: # avoid the text is too long to consume requests limit
			try:
				response_json=getJasonRes(url_text)
				categories = response_json['category_list']
				if(len(categories)>0):
						# urlMap[url[0]] = categories
					isWeapon=0
					for unit in categories:
						if int(unit['relevance'])>=50:
							if unit['code'] in codeDict:
								isWeapon=1
								urlMap[url_text]="1 "+url_text
								weapon_counter=weapon_counter+1
								break
					if isWeapon==0:
						urlMap[url_text]="0 "+url_text
					
					print weapon_counter,url_text
					print urlMap[url_text]
					print "=============================="
				else:
					urlMap[url_text] = "Non-classification"
					notfound=notfound+1
					print "Not Found1", notfound
					print "=============================="
			except KeyError:
				error_count=error_count+1
				print "KeyError",error_count
				print "=============================="

			print "\n"	


# output summary:
print "******statics*************"
print "weapon related: ",weapon_counter
print "total :",len(urlMap)

nonclass_counter=0

# Write to files
for key in urlMap:
	if urlMap[key]!= "Non-classification":
		text_file.write("{0}\n\n".format(urlMap[key]))
	# print key, urlMap[key]
	# text_file.write("{0}\n{1}\n*=*=*=\n".format("url*: "+key, urlMap[key]))
	else:
		nonclass_counter=nonclass_counter+1
print "Non-classification: ", nonclass_counter
text_file.close();

