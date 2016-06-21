#!/usr/bin/python
# -*- coding: utf-8 -*-

# Marieke van Erp 
# June 2016 
# To do: fix externalreferences formatting to comply with NAF spec
# To do: Dutch translations for Mr. & Mrs. etc

from KafNafParserPy import *
import sys
import re 
import urllib 
import datetime

infile = open(sys.argv[1],"r")
my_parser = KafNafParser(infile)
logfile = open('logfileTC_test.txt', 'a')
logNIL = open ('logfileNIL.txt', 'a')

# Gather all words 
words = {}
for word in my_parser.get_tokens():
	words[word.get_id()] = word.get_text()

# Gather all terms 
terms = {}
sent = {} 
for term in my_parser.get_terms():
	terms[term.get_id()] = ""
	for span in term.get_span():
		terms[term.get_id()] =  terms[term.get_id()] + words[span.get_id()] + " "

# get entities and store them into a dictionary  
spans = {}	
refs = {}
entity_mention = {}
entity_ref = {}  
for entity in my_parser.get_entities():	
	for reference in entity.get_references():
		idx = 0
		for span in reference.get_span():
			if idx is 0:
				entity_mention[entity.get_id()] = []
				entity_mention[entity.get_id()].append(terms[span.get_id()])
				entity_ref[entity.get_id()] = "NIL"
			else:
				entity_mention[entity.get_id()].append(terms[span.get_id()])				
			for reference in entity.get_external_references():
				if len(reference.get_reference()) > 1:	
					entity_ref[entity.get_id()] = reference.get_reference()
					break
			idx=+1

darkies = {}
enlightened = {}		
for item in entity_mention:
	if "NIL" in entity_ref[item]:  
		darkies[item] = "".join(entity_mention[item])
		print >>logNIL, sys.argv[1], darkies[item].encode('utf8')
	else:
		enlightened[item] = "".join(entity_mention[item]) 

cleanup = {} 
new_references = {} 		
# This is where you are going to try to find some matches 
# First we want to know if there are light entities that overlap with dark entities 
for item in darkies.keys():
	for entity in enlightened:
		if item == entity:
			continue
		if darkies[item] == enlightened[entity]:
			continue 
		search_pattern = re.escape(darkies[item].rstrip())
		matcher = re.escape(enlightened[entity].rstrip())
		m = re.search(search_pattern, matcher)
		if m:
			externalreferenceslayer = CexternalReferences()
			new_ext_reference = CexternalReference()
			new_ext_reference.set_resource('DoubleLinkEntities')
			try:
				new_ext_reference.set_reference(entity_ref[entity])
				logstring = sys.argv[1] + "\t" + 'DoubleLinkEntities' + "\t" + item + "\t" + darkies[item] + "\t" + entity + "\t" + enlightened[entity] + "\t" + entity_ref[entity]
				print >>logfile, logstring
				#print logstring
				cleanup[item] = darkies[item]
				new_references[item] = entity_ref[entity]
			except:
				pass
			new_ext_reference.set_confidence('1.0')
			my_parser.get_entity(item).add_external_reference(new_ext_reference)

for i in cleanup:
	enlightened[i] = darkies[i]
	entity_ref[i] = new_references[i]  
	del darkies[i]

cleanup = {}
# Let's see if we can also match things with Mr. or Mrs. blabla to the full name 
for item in darkies.keys():
	if "Mr " in darkies[item]:
	#	print "whoopwhoop!", darkies[item]
		search = darkies[item].replace("Mr ", "")
	elif "Mr. " in darkies[item]:
		search = darkies[item].replace("Mr. ", "")
	elif "Mrs " in darkies[item]:
		search = darkies[item].replace("Mrs ", "")
	elif "Mrs. " in darkies[item]:
		search = darkies[item].replace("Mrs. ", "")
	elif "Ms " in darkies[item]:
		search = darkies[item].replace("Ms ", "")
	elif "Ms. " in darkies[item]:
		search = darkies[item].replace("Ms. ", "")
	elif "Prof. " in darkies[item]:
		search = darkies[item].replace("Prof. ", "")
	elif "Prof " in darkies[item]:
		search = darkies[item].replace("Prof ", "")	
	elif "Baroness " in darkies[item]:
		search = darkies[item].replace("Baroness ", "")
	elif "Lord " in darkies[item]:
		search = darkies[item].replace("Lord ", "")
	else:
		continue
	for entity in enlightened:
	#	print "enlightened:", enlightened[entity]
		search_pattern = re.escape(search.rstrip())
		matcher = re.escape(enlightened[entity].rstrip())
		m = re.search(search_pattern, matcher)
	#	print "pattern", search_pattern, matcher
		#	print "blabla", entity, enlightened[entity]
		if entity == item:
			continue
		if darkies[item] == enlightened[entity]:
			continue
		if m:
			externalreferenceslayer = CexternalReferences()
			new_ext_reference = CexternalReference()
			new_ext_reference.set_resource('DoubleLinkEntities')
			try:
				new_ext_reference.set_reference(entity_ref[entity])
				logstring = sys.argv[1] + "\t" + 'DoubleLinkEntitiesTitles' + "\t" + item + "\t" + darkies[item] + "\t" + entity + "\t" + enlightened[entity] + "\t" + entity_ref[entity]
				print >>logfile, logstring
			#	print logstring
				cleanup[item] = darkies[item]
				new_references[item] = entity_ref[entity]	
			except:
				pass
			new_ext_reference.set_confidence('1.0')
			my_parser.get_entity(item).add_external_reference(new_ext_reference)	

for i in cleanup:
	enlightened[i] = darkies[i]
	entity_ref[i] = new_references[i]  
	del darkies[i]
	
cleanup = {}
# Then we also want to see if we can cluster the dark entities together and generate 
# an instance ID for them
for item in darkies.keys():
	for entity in darkies:
		search_pattern = re.escape(darkies[item].rstrip())
		m = re.search(search_pattern, darkies[entity], re.IGNORECASE)
		if m:
			if item == entity:
				continue
			if darkies[item] == darkies[entity]:
				continue
			else:
				reference = ''
				if len(darkies[item]) > len(darkies[entity]):
					reference = 'newsreader_entity-' + darkies[item]
				else:
					reference = 'newsreader_entity-' + darkies[entity]
				reference = reference.rstrip()
				reference = urllib.quote_plus(reference.encode('utf8'))
		#		print darkies[item], darkies[entity]
				externalreferenceslayer = CexternalReferences()
				new_ext_reference = CexternalReference()
				new_ext_reference.set_resource('DoubleLinkEntities')
				try:
					new_ext_reference.set_reference(reference)	
					logstring = sys.argv[1] + "\t" + 'Darkies' + "\t" + item + "\t" + darkies[item] + "\t" + entity + "\t" + darkies[entity] + "\t" + reference
					print >>logfile, logstring 
				#	print logstring
					cleanup[item] = darkies[item]
					new_references[item] = reference
				except:
					pass
				new_ext_reference.set_confidence('1.0')
				my_parser.get_entity(item).add_external_reference(new_ext_reference)
	
for i in cleanup:
	enlightened[i] = darkies[i]
	entity_ref[i] = new_references[i]  
	del darkies[i]	
	
## Create header info
lp = Clp()
lp.set_name('vua-intra-document-entity-coference-for-linking')
lp.set_version('1.0')

lp.set_timestamp()
my_parser.add_linguistic_processor('entities', lp)	

# Output the modified NAF file			
my_parser.dump()					
