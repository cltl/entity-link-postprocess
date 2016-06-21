#!/usr/bin/python
# -*- coding: utf-8 -*-

# Marieke van Erp 
# June 2016 
# To do: fix externalreferences formatting to comply with NAF spec

from KafNafParserPy import *
import sys
import re 
import urllib 
import datetime

infile = open(sys.argv[1],"r")
my_parser = KafNafParser(infile)
logfile = open('logfile.txt', 'a') # Make sure to empty this before you rerun 
logNIL = open ('logfileNIL.txt', 'a') # Make sure to empty this before you rerun 

dominants = {}
# read in Dominant Entities that have been linked 
# This file should be a tab separated file with a surface form and a link e.g.:
# John McEnroe	http://dbpedia.org/resource/John_McEnroe
with open(sys.argv[2] , "r") as f:
	for line in f:
		line = line.rstrip()
		elements = line.split("\t")
		dominants[elements[0]] = elements[1] 


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

for item in darkies.keys():
	if darkies[item] in dominants:
		externalreferenceslayer = CexternalReferences()
		new_ext_reference = CexternalReference()
		new_ext_reference.set_resource('DominantDoubleLinkEntities')
		try:
			new_ext_reference.set_reference(dominants[darkies[item]])
			logstring = sys.argv[1] + "\t" + 'LinkDarkEntitiesCrossDocument' + "\t" + item + "\t" + darkies[item] + "\t" + item + "\t" + dominants[item] + "\t" + entity_ref[entity]
			print >>logfile, logstring
			#	print logstring
			#cleanup[item] = darkies[item]
			new_references[item] = entity_ref[entity]	
		except:
			pass
		new_ext_reference.set_confidence('1.0')
		my_parser.get_entity(item).add_external_reference(new_ext_reference)	

	
## Create header info
lp = Clp()
lp.set_name('vua-cross-document-entity-coference-for-linking')
lp.set_version('1.0')

lp.set_timestamp()
my_parser.add_linguistic_processor('entities', lp)	

# Output the modified NAF file			
my_parser.dump()					
