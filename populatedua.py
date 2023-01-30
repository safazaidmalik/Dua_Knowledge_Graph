# -*- coding: utf-8 -*-
"""PopulateDua.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1J8-gzjOZpMEvDDmv59Piv7gK_Qek9PTu

# Populate Dua Graph

## Installing required Packages
"""

# !pip install rdflib
# !pip install SPARQLWrapper
# !pip install owlready2
# !pip install PyArabic

"""## Importing packages"""
import utils
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import FOAF, XMLNS, XSD, RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

import csv, re, unicodedata
# Utility ftn.s and data
############################################################
# import pyarabic.araby as araby
# import pyarabic.number as number
# from pyarabic.araby import strip_harakat, strip_tashkeel, strip_tatweel, normalize_hamza, tokenize, sentence_tokenize, is_arabicrange

"""## Loading Graphs"""

g_Hadith = Graph()
g_Hadith.parse('ontologies/SemanticHadithKG.ttl', format = 'turtle')
hn = Namespace('http://www.i-knex.com/ontology/hadith#')

g_Quran = Graph()
g_Quran.parse('ontologies/quran_data_full.ttl', format = 'turtle')
qn = Namespace ('http://quranontology.com/Resource/')

g_dua = Graph()
g_dua.parse('ontologies/dua_ontology_schema.ttl', format = 'turtle')
n = Namespace('http://www.semanticweb.org/szm/dua-ontology#')

"""### Quran Chapters List"""

q_surah_lis = [
['الفاتحة','The Opening'],
['البقرة','Al-Baqara'],
['آل عمران','Aal-i-Imraan'],
['لنساء','An-Nisa'],
['المائدة"','The Table'],
['الأنعام','The Cattle'],
['الأعراف',"Al-A'raaf"],
['الأنفال','The Spoils of War'],
['التوبة','At-Tawba'],
['يونس"','Jonas'],

['هود','Hud'],
['يوسف',"Joseph"],
['الرعد','The Thunder'],
['ابراهيم','Abraham'],
['الحجر','Al-Hijr'],
['النحل',"An-Nahl"],
['الإسراء','Al-Israa'],
['الكهف','Al-Kahf'],
['مريم','Mary'],
['طه',"Taa-Haa"],


['الأنبياء','The Prophets'],
['الحج',"The Pilgrimage"],
['المؤمنون','Al-Muminoon'],
['النور','An-Noor'],
['الفرقان','Al-Furqaan'],
['الشعراء',"Ash-Shu'araa"],
['النمل','An-Naml'],
['القصص','The Stories'],
['العنكبوت','The Spider'],
['الروم',"Ar-Room"],


['لقمان','Luqman'],
['السجدة',"As-Sajda"],
['الأحزاب','Al-Ahzaab'],
['سبإ','Saba'],
['فاطر','The Originator'],
['يس',"Yaseen"],
['الصافات','As-Saaffaat'],
['ص','Saad'],
['الزمر','Az-Zumar'],
['غافر',"Al-Ghaafir"],


['فصلت','Explained in detail'],
['الشورى',"Ash-Shura"],
['الزخرف','Ornaments of gold'],
['الدخان','Ad-Dukhaan'],
['الجاثية','Crouching'],
['الأحقاف',"Al-Ahqaf"],
['محمد','Muhammad'],
['الفتح','Al-Fath'],
['الحجرات','Al-Hujuraat'],
['ق',"Qaaf"],


['الذاريات','The Winnowing Winds'],
['الطور',"The Mount"],
['النجم','An-Najm'],
['القمر','Al-Qamar'],
['الرحمن','Ar-Rahmaan'],
['الواقعة',"The Inevitable"],
['الحديد','Al-Hadid'],
['المجادلة','Al-Mujaadila'],
['الحشر','The Exile'],
['الممتحنة',"Al-Mumtahana"],


['الصف','The Ranks'],
['الجمعة',"Al-Jumu'a"],
['المنافقون','Al-Munaafiqoon'],
['التغابن','Mutual Disillusion'],
['الطلاق','At-Talaaq'],
['التحريم',"At-Tahrim"],
['الملك','Al-Mulk'],
['القلم','Al-Qalam'],
['الحاقة','Al-Haaqqa'],
['المعارج',"The Ascending Stairways"],


['نوح','Nooh'],
['الجن',"Al-Jinn"],
['المزمل','Al-Muzzammil'],
['المدثر','Al-Muddaththir'],
['القيامة','Al-Qiyaama'],
['الانسان',"Man"],
['المرسلات','The Emissaries'],
['النبإ','An-Naba'],
['النازعات','Those who drag forth'],
['عبس',"He frowned"],


['التكوير','At-Takwir'],
['الإنفطار',"Al-Infitaar"],
['المطففين','Al-Mutaffifin'],
['الإنشقاق','Al-Inshiqaaq'],
['البروج','Al-Burooj'],
['الطارق',"At-Taariq"],
['الأعلى',"Al-A'laa"],
['الغاشية','Al-Ghaashiya'],
['الفجر','Al-Fajr'],
['البلد',"Al-Balad"],


['الشمس','Ash-Shams'],
['الليل',"Al-Lail"],
['الضحى','The Morning Hours'],
['الشرح','Ash-Sharh'],
['التين','The Fig'],
['العلق',"The Clot"],
['القدر',"The Power, Fate"],
['البينة','The Evidence'],
['الزلزلة','Az-Zalzala'],
['العاديات',"Al-Aadiyaat"],


['القارعة','The Calamity'],
['التكاثر',"Competition"],
['العصر','The Declining Day, Epoch'],
['الهمزة','The Traducer'],
['الفيل','Al-Fil'],
['قريش',"Quraish"],
['الماعون',"Almsgiving"],
['الكوثر','Al-Kawthar'],
['الكافرون','The Disbelievers'],
['النصر',"Divine Support"],


['المسد',"Al-Masad"],
['الإخلاص','Sincerity'],
['الفلق','Al-Falaq'],
['الناس',"Mankind"]

]
"""### Function to Find Dua Category (returns category id(s) for a dua id)"""
def add_dua_category(dua_cat_map_file, dua_categories_dict, duas_dict):

    with open(dua_cat_map_file, 'r', encoding='utf-8', errors='replace') as file:
        csvreader = csv.DictReader(file)
        print("csvreader rows:\n")
        for row in csvreader:
            if str(row["category_id"]) != '0' and str(row["dua_id"]):       # ignore category_id = 0
                print(row)

                try:

                    dua_IRI = duas_dict[Literal(row["dua_id"], datatype = XSD.nonNegativeInteger)]
                    cat_IRI = dua_categories_dict[Literal(row["category_id"], datatype=XSD.nonNegativeInteger)]

                    if dua_IRI != "Sample":
                        
                        g_dua.add((dua_IRI, FOAF.topic, cat_IRI))
                        print("Added Dua to Category : \n", dua_IRI, FOAF.topic, cat_IRI, '\n')                
                    else:
                        print("Dua with dua_id: ", Literal(row["dua_id"], datatype = XSD.nonNegativeInteger), " is a Sample dua.")
                        continue
                except Exception as e:
                    print("Sample dua: ", dua_IRI,  ". Category not linked.")


def add_dua_occasion(dua_occasion_map_file,dua_occasions_dict, duas_dict):
    with open(dua_occasion_map_file, 'r', encoding='utf-8', errors='replace') as file:
        csvreader = csv.DictReader(file)
        print("csvreader rows:\n")
        for row in csvreader:
            if str(row["occasion_id"]) and str(row["dua_id"]):
                print(row)

                try:
                    dua_IRI = duas_dict[Literal(row["dua_id"], datatype = XSD.nonNegativeInteger)]
                    occasion_IRI = dua_occasions_dict[Literal(row["occasion_id"], datatype=XSD.nonNegativeInteger)]
                    print("Occasion IRI = ", occasion_IRI)

                    if dua_IRI != "Sample":                        
                        # g_dua.add((occasion_IRI, RDF.type, n.Occasion))
                        prescription = BNode()
                        g_dua.add((dua_IRI, n.duaHasPrescription, prescription))
                        g_dua.add((prescription, n.prescribedForOccasion, occasion_IRI))
                        g_dua.add((prescription, n.prescribedRepetitions, Literal(row["repetitions"], datatype=XSD.string)))
                        g_dua.add((prescription, n.prescribedMerit, Literal(row["merit"], datatype=XSD.string)))

                        print("Added Dua to prescribed occasion,repetitions and merit : \n", dua_IRI, n.prescribedForOccasion, occasion_IRI, '\n')
                        print(dua_IRI, n.prescribedRepetitions, row["repetitions"], '\n')
                        print(dua_IRI, n.prescribedMerit, row["merit"], '\n')

                    else:
                        print("Dua with dua_id: ", Literal(row["dua_id"], datatype = XSD.nonNegativeInteger), " is a Sample dua.")
                        continue
                except Exception as e:
                    print("Sample dua: ", dua_IRI,  ". Category not linked.")


"""### Function to Add Quranic References"""

def find_add_quran_ref(q_dua, surah_index, complete_ref, norm_surah_name, orig_surah_name):

    verse_index = int(re.sub('[^0-9]+', '', complete_ref))

    query = """
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX qo:<http://quranontology.com/Resource/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT Distinct ?verse ?vIndex ?cIndex
    {
      ?verse a qo:Verse.
      ?verse qo:VerseIndex ?vIndex.
      ?verse qo:ChapterIndex ?cIndex.
      ?verse qo:IsPartOf ?chapter.
      ?chapter rdfs:label ?chapName. 
    }
    """

    qres = g_Quran.query(query, initBindings={"vIndex": Literal(verse_index, datatype=XSD.nonNegativeInteger),
                                              "cIndex": Literal(surah_index, datatype=XSD.nonNegativeInteger) })

    
    for row in qres:
        g_dua.add((q_dua, qn.IsPartOf, row.verse))
        print("Added Quranic Reference : \n", q_dua, qn.IsPartOf, row.verse, '\n')

"""### Function to add Hadith References"""

def find_add_hadith_ref(h_dua, hadith_IRI):
    query = """
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX :<http://www.i-knex.com/ontology/hadith#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT distinct ?hadith WHERE
    {
      ?hadith rdf:type :Hadith.
      FILTER (?hadith = <"""+hadith_IRI+""">)
    }
    """
    qres = g_Hadith.query(query)

    for row in qres:
        g_dua.add((h_dua, hn.isPartOfHadith, row.hadith))
        print("Added Hadith Reference : \n", f'\n{h_dua} {hn.isPartOfHadith} {row.hadith} \n')


"""### Function to add Occasions"""
def add_Occasions(file_name):
    occasion_id_iri_dict = dict()
    # Make categories first: Read dua_category_map-v80.csv
    with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
        csvreader = csv.DictReader(file)
        count = 0
        for row in csvreader:
            occasion = URIRef(str(n)+"Occasion-"+str(row["occasion_id"]))
            g_dua.add((occasion, RDF.type, n.Occasion))
            g_dua.add((occasion, n.occasionId, Literal(row["occasion_id"], datatype=XSD.nonNegativeInteger)))
            g_dua.add((occasion, n.occasionEnglishTitle, Literal(row["title_en"], datatype = XSD.string)))
            g_dua.add((occasion, n.occasionUrduTitle, Literal(row["title_ur"], datatype = XSD.string)))

            occasion_id_iri_dict[Literal(row["occasion_id"], datatype=XSD.nonNegativeInteger)]= occasion
            # key: Literal version of occasion id
            # value: IRI of the occasion individual
        return occasion_id_iri_dict    

"""### Function to add Categories"""

def add_Categories(file_name):
    cat_id_iri_dict = dict()
    # Make categories first: Read dua_category_map-v80.csv
    with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
        csvreader = csv.DictReader(file)
        count = 0
        for row in csvreader:
            cat = URIRef(str(n)+ "Category-"+str(row["category"]))
            g_dua.add((cat, RDF.type, n.DuaCategory))
            g_dua.add((cat, n.categoryId, Literal(row["id"], datatype=XSD.nonNegativeInteger)))
            g_dua.add((cat, n.categoryUrduTitle, Literal(row["title_ur"], datatype = XSD.string)))
            g_dua.add((cat, n.categoryEnglishTitle, Literal(row["title_en"], datatype = XSD.string)))

            cat_id_iri_dict[Literal(row["id"], datatype=XSD.nonNegativeInteger)]= cat
            # key: Literal version of category id
            # value: IRI of the category individual
        return cat_id_iri_dict

"""### Function to add Duas"""


def add_duas(file_name):
    dua_id_iri_dict = dict()
    count = 0
    
    with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
        csvreader = csv.DictReader(file)

        with open('./IRIConstruction/Dua_modified.csv', 'r', encoding='utf-8', errors='replace') as file2:
            csvreader2 = csv.DictReader(file2)

            for row in csvreader:
                
                try:
                    data = next(csvreader2)
                except StopIteration:
                    break
                
                if row["duaArabic"] != "Sample":
                    dua = URIRef(str(n)+"Dua-"+str(row["duaId"]))
                    g_dua.add((dua, RDF.type, n.Dua))

                    g_dua.add((dua, n.duaId, Literal(row["dua_id"], datatype = XSD.nonNegativeInteger)))

                    dua_id_iri_dict[Literal(row["dua_id"], datatype = XSD.nonNegativeInteger)] = dua

                    g_dua.add((dua, n.duaUrduTitle, Literal(row["duaTitle_ur"], datatype = XSD.string)))
                    g_dua.add((dua, n.duaEnglishTitle, Literal(row["duaTitle_en"], datatype = XSD.string)))

                    g_dua.add((dua, n.duaArabicText, Literal(row["duaArabic"], datatype = XSD.string)))
                    g_dua.add((dua, n.duaEnglishText, Literal(row["dua_en"], datatype = XSD.string)))
                    g_dua.add((dua, n.duaUrduText, Literal(row["dua_ur"], datatype = XSD.string)))

                    if row["duaType_en"] == "Qurani Dua":
                        g_dua.add((dua, RDF.type, n.QuranicDua))
                        g_dua.add((dua, n.duaType, Literal("Qurani Dua", datatype = XSD.string)))

                        surah_index = 1
                        for s in q_surah_lis:
                            if row["duaReference_ur"].find('-') == -1:
                                # not considering verse ranges for now

                                tokenized_csv_ref = utils.tokenize(row["duaReference_ur"], conditions=utils.is_arabicrange, morphs=utils.strip_tashkeel)
                                normalized_csv_ref = utils.normalizeArabic(utils.deNoise(row["duaReference_ur"]))
                                tokenized_surah = utils.tokenize(s[0], conditions=utils.is_arabicrange, morphs=utils.strip_tashkeel)
                                normalized_surah = utils.normalizeArabic(utils.deNoise(s[0]))                
                                csv_ref_arabic = re.sub('[0-9 ()]+', '', utils.normalizeArabic(utils.deNoise(row["duaReference_ur"])))

                                if normalized_csv_ref.find(normalized_surah) != -1 and abs(len(csv_ref_arabic)-len(normalized_surah)) <= 2:
                                    find_add_quran_ref(dua, surah_index, normalized_csv_ref, normalized_surah, s[0])
                                    count+=1
                            else:
                                # considering verse ranges now, but not commas
                                if row["duaReference_ur"].find(',') == -1:

                                    tokenized_csv_ref = utils.tokenize(row["duaReference_ur"], conditions=utils.is_arabicrange, morphs=utils.strip_tashkeel)
                                    normalized_csv_ref = utils.normalizeArabic(utils.deNoise(row["duaReference_ur"]))
                                    ref_verse_range =  re.sub('[^0-9\-]', '', normalized_csv_ref)
                                    verse_range_ends = ref_verse_range.split('-')
                                    for i in range(len(verse_range_ends)):
                                        verse_range_ends[i] = int(verse_range_ends[i])
                                    tokenized_surah = utils.tokenize(s[0], conditions=utils.is_arabicrange, morphs=utils.strip_tashkeel)
                                    normalized_surah = utils.normalizeArabic(utils.deNoise(s[0]))
                                    csv_ref_arabic = re.sub('[0-9 ()]+', '', utils.normalizeArabic(utils.deNoise(row["duaReference_ur"])))

                                    if normalized_csv_ref.find(normalized_surah) != -1 and abs(len(csv_ref_arabic)-len(normalized_surah)) <= 2:
                                        for v in verse_range_ends:
                                            pos = re.search(r"\d", normalized_csv_ref)
                                            print(pos.start())
                                            new_normalized_csv_ref = re.sub('[0123456789-]','',normalized_csv_ref)
                                            new_normalized_csv_ref = new_normalized_csv_ref[:pos.start()] + str(v) + new_normalized_csv_ref[pos.start():]
                                            print(new_normalized_csv_ref)
                                            find_add_quran_ref(dua, surah_index, new_normalized_csv_ref, normalized_surah, s[0])
                            surah_index +=1
                    else:
                        g_dua.add((dua, RDF.type, n.HadithDua))
                        g_dua.add((dua, n.duaType, Literal(row["duaType_en"], datatype = XSD.string)))
                        if data["Dua_IRI"]:
                            find_add_hadith_ref(dua, data["Dua_IRI"])

                else:
                    dua_id_iri_dict[Literal(row["dua_id"], datatype = XSD.nonNegativeInteger)] = "Sample"

    print("Counts of found surahs = ", count)
    return dua_id_iri_dict
    ####################################################################################

"""### Adding Categories And References to the dua Graph"""

categories_dict = add_Categories('./data/Duaein Data - For KG - revisedCategories-v57.csv')

# file to be added upon annotation - should contain cols as such:
# occasionID, occasionTitle (),  
occasions_dict = add_Occasions('./data/Duaein Data - For KG - dua_Occasions.csv')


duas_dict = add_duas('./data/Duaein Data - For KG - duas-test-v80.csv')
add_dua_category('./data/Duaein Data - For KG - dua_category_map-v80.csv', categories_dict, duas_dict)
add_dua_occasion('./data/Duaein Data - For KG - dua_occasion_map.csv', occasions_dict, duas_dict)

"""### Quering the graph to see if the references are added"""

qres = g_dua.query(
"""
    PREFIX : <http://www.semanticweb.org/szm/dua-ontology#>
    PREFIX hn: <http://www.i-knex.com/ontology/hadith#>
    SELECT ?s ?p ?o 
    WHERE {
        ?s hn:isPartOfHadith ?o .
    }
"""
)

print('\n Added Hadith References in the Dua Graph \n')
for row in qres:
    print(f'{row.s} isPartOfHadith {row.o} ')

qres = g_dua.query(
"""
    PREFIX : <http://www.semanticweb.org/szm/dua-ontology#>
    PREFIX hn: <http://www.i-knex.com/ontology/hadith#>
    PREFIX qn: <http://quranontology.com/Resource/>
    SELECT ?s ?p ?o 
    WHERE {
        ?s qn:IsPartOf ?o .
    }
"""
)

print('\n Added Quranic References in the Dua Graph \n')
for row in qres:
    print(f'{row.s} isPartOf {row.o} ')

"""## Saving the Graph"""

g_dua.serialize(destination='./ontologies/populated_dua_graph.ttl', format='turtle')


