import couchdb
from couchdb.design import ViewDefinition
from couchdb import design
import time

user = "admin"
password = "cccteam8"
couchserver = couchdb.Server("http://%s:%s@45.76.119.0:5984/" % (user, password))
dbname = "melb_tweets"

if dbname in couchserver:
    db = couchserver[dbname]
else:
    db = couchserver.create(dbname)


reduce_method = '_stats'

sports_map = 'function (doc) { if(doc.postcode>=3000) var v=0;pattern=/(golf|flag in hole)|\u26F3|sketaboard|skater|\uD83C\uDFC2|\u26F8/i,doc.text.match(pattern)&&(v=1),pattern=/(basketball)|\uD83C\uDFC0|\u26F9|(soccer)|\u26BD|(baseball)|\u26BE|(volleyball)|\uD83C\uDFD0|(football)|\uD83C\uDFC8/i,doc.text.match(pattern)&&(v=1),pattern=/(jog|run|marathon)|(frisbee game)|\uD83C\uDFC3/i,doc.text.match(pattern)&&(v=1),pattern=/(biking|bike|bicycle|bicycling)|\uD83D\uDEB4|tennis|\uD83D\uDEB5|\uD83C\uDFBE|badminton|\uD83C\uDFF8/i,doc.text.match(pattern)&&(v=1),emit(doc.postcode,v)}'
view = ViewDefinition('designDoc','sports',
'''
function(doc) {
v = 0

regex=/(#| |^)(golf|flag in hole)( |ing|$|s|es|ed)|\uD83C\uDFCC|\u26F3/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(swim|swimming)( |$|s|es|ed)|\uD83C\uDFCA/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(biking|bike|bicycle|bicycling)( |$|s|es|ed|d)|\uD83D\uDEB4|\uD83D\uDEB5/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(soccer)( |$|s|es|ed)|\u26BD/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(baseball)( |$|s|es|ed)|\u26BE/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(basketball)( |$|s|es|ed)|\uD83C\uDFC0/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(volleyball)( |$|s|es|ed)|\uD83C\uDFD0/i
if(doc.text.match(regex))
v=1

regex=/(#| |^)(football)( |$|s|es|ed)|\uD83C\uDFC8|\uD83C\uDFC9/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(tennis)( |$|s|es|ed)|\uD83C\uDFBE/i
if(doc.text.match(regex))
v=1

regex=/(#| |^)(bowling)( |$|s|es|ed)|\uD83C\uDFB3/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(pingpong|table tennis)( |$|s|es|ed)|\uD83C\uDFD3/i
if(doc.text.match(regex))
v=1

regex=/(#| |^)(badminton)( |$|s|es|ed)|\uD83C\uDFF8/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(skate|skating)( |$|s|es|ed|d)|\u26F8/i
if(doc.text.match(regex))
v=1

regex=/(#| |^)(jogging|running|run)( |$|s|es|ed)|\uD83C\uDFC3/i
if(doc.text.match(regex)) 
v=1

regex=/(#| |^)(gym)/i
if(doc.text.match(regex)) 
v=1

if(doc.postcode>=3000)
emit(doc.postcode,v)

}
''',reduce_method)
print(view.sync(db))
print('Creating View......')
try:
	for doc in db.view('designDoc/sports'):
	        print('complete')
	        break
except couchdb.http.ServerError:
	time.sleep(300)
print('Start to creating next view')


#suburbSentiment view
suburbSentiment_map = "function (doc) {  if (doc.postcode >=3000) emit(doc.postcode, doc.sentiment); }"

view = ViewDefinition('designDoc', 'suburbSentiment',suburbSentiment_map,reduce_method)
print(view.sync(db))
print('Creating View......')
try:
	for doc in db.view('designDoc/suburbSentiment'):
	        print('complete')
	        break
except couchdb.http.ServerError:
	time.sleep(300)
print('Start to creating next view')


#lga view
lga_map = "function (doc) { if (doc.lga_code >= 1000 && Math.abs(doc.sentiment) >= 0.01)  emit([doc.lga_code], doc.sentiment) }"

view = ViewDefinition('designDoc', 'lga',lga_map,reduce_method)
print(view.sync(db))
print('Creating View......')
try:
	for doc in db.view('designDoc/lga'):
	        print('complete')
	        break
except couchdb.http.ServerError:
	time.sleep(300)
print('Start to creating next view')




#badwords view
badwords_map = "function (doc) { if (doc.postcode >=3000)  emit(doc.postcode, doc.bad_words) }"

view = ViewDefinition('designDoc', 'badwords',badwords_map,reduce_method)
print(view.sync(db))
print('Creating View......')
print(db.view('designDoc/badwords'))
try:
	for doc in db.view('designDoc/badwords'):
	        print('complete')
	        break
except couchdb.http.ServerError:
	time.sleep(300)
print('Start to creating next view')


# heatmap view
heatmap_map = "function (doc) { if (doc.postcode >=3000)  emit([doc.day, doc.hour], doc.sentiment) }"

view = ViewDefinition('designDoc', 'heatmap',heatmap_map,reduce_method)
print(view.sync(db))
print('Creating View......')
print(db.view('designDoc/heatmap'))
try:
	for doc in db.view('designDoc/heatmap'):
	        print('complete')
	        break
except couchdb.http.ServerError:
	time.sleep(300)
print('Start to creating next view')


# sentimentFilters View
sentimentFilters_map = "function (doc) { if (doc.postcode >= 3000 && Math.abs(doc.sentiment) >= 0.01)  emit([doc.day, doc.hour], doc.sentiment) }"

view = ViewDefinition('designDoc', 'sentimentFilters',sentimentFilters_map,reduce_method)
print(view.sync(db))
print('Creating View......')
print(db.view('designDoc/sentimentFilters'))
try:
	for doc in db.view('designDoc/sentimentFilters'):
	        print('complete')
	        break
except couchdb.http.ServerError:
	time.sleep(300)
print('All complete')







