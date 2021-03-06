Entity Link Postprocessing Scripts 
===================================

The scripts in this repo are designed to mitigate some of the entity linking module's blatant errors by focusing on most frequent entities in a domain (dominant entities) and naming variations (John Smith/Mr. Smith).

The scripts expect NAF input files with entity recognition and entity linking layers. The dominantEntities.py script requires a list of dominant entities in the domain which needs to be precompiled. The scripts are to be invoked in the following order:

1. python relinkDarkEntities.py INPUTFILE 
-------------------------------------------
This script takes a NAF file, and for every entity without a link, it checks whether there are entity mentions that show a high overlap with entity mentions that do have a link, after which that link is added to the previously unlinked entity. For example if the entity "David Cameron" has a link, but "Cameron" mentioned in another part of the article doesn't, then the link from "David Cameron" is added to the "Cameron" mention. It also adds links for "Mr. So and so" and "Mrs. So and so" if there is an entity mention "So and so" that has a link. 

2: python dominantEntities.py INPUTFILE DOMINANTENTITIESFILE
--------------------------------------------------------------
This script reads in a TSV file containing entity links derived from the NAF files that need to be corrected (column 1) to thecorrect link. For example for the political domain, a link dbpedia:Dave_Cameron_(footballer) may to be corrected to dbpedia:David_Cameron_(polician). The dominant entities file would thus contain the following line: 
dbpedia:Dave_Cameron_(footballer) dbpedia:David_Cameron_(politician)

Previous links are not overwritten, but a new link is added with the marker "DominantEntities" to indicate it was generated by this module. 

3. python linkDarkEntitiesCrossDocument.py INPUTFILE CROSSDOCENTITIES
--------------------------------------------------------------
This is the most experimental of the postprocessing scripts. It takes the output of the relinkDarkEntities.py and optionally dominantEntities.py to try to link entity mentions in a file that couldn't be fixed by the first two steps. 
The CROSSDOCENTITIES list can be obtained by performing the following command on the logfile of relinkDarkEntities.py <INPUTFILE>:
cut -f4,7 < logfile > CROSSDOCENTITIES 

Optionally the list can be filtered to only contain entity links from the DOMINANTENTITIESFILE:
cut -f2 < DOMINANTENTITIESFILE > DOMINANTENTITIES 
grep -f DOMINANTENTITIES < CROSSDOCENTITIES > CROSSDOCENTITIES_ONLYDOMINANTS


Warning
-------
This is still work in progress.

Comments & suggestions can be directed to: marieke.van.erp@vu.nl
