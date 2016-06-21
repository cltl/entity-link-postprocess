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
logfile = open('DominantEntitiesLogfile.txt', 'a') # 

# Read in the dominant entities and store in a dictionary 
# The file should be a tsv in with the non-domimant entity in the first position, and 
# the entity to which it should be linked in the second position e.g.:
# http://dbpedia.org/resource/not_very_famous_David_Cameron	http://dbpedia.org/resource/David_Cameron
doms = {}
with open(sys.argv[2], "r") as ins:
	for line in ins:
		line = line.rstrip()
		elements = line.split("\t")
		elements[0] = elements[0].rstrip()
		doms[elements[0]] = elements[1]

#for el in doms:
#	print el, doms[el]
	
# get entities and store them into a dictionary  
spans = {}	
refs = {}
entity_mention = {}
entity_ref = {}  
for entity in my_parser.get_entities():
	all = sys.argv[1] + "\t" + entity.get_id() 
	print >>Totallogfile, all
	for ref in entity.get_references():
		for span in ref.get_span():				
			for reference in entity.get_external_references():
				if len(reference.get_reference()) > 1:
					if reference.get_reference() in doms:
						#print reference.get_reference(), doms[reference.get_reference()]
						new_ext_reference = CexternalReference()
						new_ext_reference.set_resource('DominantEntities')
						try:
							new_ext_reference.set_reference(doms[reference.get_reference()])
						except:
							pass
						new_ext_reference.set_confidence('1.0')
						entity.add_external_reference(new_ext_reference)
						logstring = sys.argv[1] + "\t" + "DominantEntities\t" + entity.get_id() + "\t" + reference.get_reference() + "\t" + doms[reference.get_reference()]
						print >>logfile, logstring
			




## Create header info
lp = Clp()
lp.set_name('vua-dominant-entities-for-linking')
lp.set_version('1.0')

lp.set_timestamp()
my_parser.add_linguistic_processor('entities', lp)	

# Output the modified NAF file			
my_parser.dump()					
