#!pip install rdflib
# !pip install SPARQLWrapper
# !pip install owlready2
# !pip install PyArabic

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import FOAF, XMLNS, XSD, RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

import csv, re, unicodedata
# Utility ftn.s and data
############################################################
import pyarabic.araby as araby
import pyarabic.number as number
from pyarabic.araby import strip_harakat, strip_tashkeel, strip_tatweel, normalize_hamza, tokenize, sentence_tokenize, is_arabicrange

g_Hadith = Graph()
g_Hadith.parse('SemanticHadithKG.ttl', format = 'turtle')
hn = Namespace('http://www.i-knex.com/ontology/hadith#')

g_Quran = Graph()
g_Quran.parse('quran_data_full.ttl', format = 'turtle')
qn = Namespace ('http://quranontology.com/Resource/')

g = Graph()
g.parse('dua_ontology_scehma.ttl', format = 'turtle')
n = Namespace('http://www.semanticweb.org/szm/dua-ontology#')

# def normalize_arabic(text):
#     return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

# print(normalize_hamza(strip_tatweel(strip_harakat(strip_tashkeel("الإسراء")))))
def normalize_alaf(text):
    return text.replace('إ', 'ا')


def normalizeArabic(text):
    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    return(text)

def deNormalize(text):
    alifs           = '[إأٱآا]'
    alifReg         = '[إأٱآا]'
    # -------------------------------------
    alifMaqsura     = '[يى]'
    alifMaqsuraReg  = '[يى]'
    # -------------------------------------
    taMarbutas      = 'ة'
    taMarbutasReg   = '[هة]'
    # -------------------------------------
    hamzas          = '[ؤئء]'
    hamzasReg       = '[ؤئءوي]'
    # Applying deNormalization
    text = re.sub(alifs, alifReg, text)
    text = re.sub(alifMaqsura, alifMaqsuraReg, text)
    text = re.sub(taMarbutas, taMarbutasReg, text)
    text = re.sub(hamzas, hamzasReg, text)
    return text

def deNoise(text):
    noise = re.compile(""" ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(noise, '', text)
    return text


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

def find_add_hadith_ref(h_dua, hadith_IRI):
  qres = g_Hadith.query(
    """
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX hVoc:<http://www.i-knex.com/ontology/hadith#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?hadith ?hChap ?hBook ?hCollect ?hCollectName WHERE
    {
      ?hadith a hVoc:Hadith.
      ?hadith hVoc:isPartOfChapter ?hChap.
      ?hChap hVoc:isPartOfBook ?hBook.
      ?hBook hVoc:isPartOfCollection ?hCollect.
      ?hCollect hVoc:collectionName ?hCollectName.
    }
    """
  )

  for row in qres:
    if row.hadith.toPython() == hadith_IRI:
      g.add((h_dua, hn.isPartOfHadith, row.hadith))
      g.add((row.hadith, hn.isPartOfChapter, row.hChap))
      g.add((row.Chap, hn.isPartOfBook, row.hBook))
      g.add((row.hBook, hn.isPartOfCollection, row.hCollect))
      g.add((row.hCollect, hn.collectionName, row.hCollectName))
      
      print("Linked dua: ", h_dua.toPython())
      # print(row.hadith.toPython(), type(row.hadith.toPython()))


      # if row.hadith.toPython() == verse_index:
      #   if row.chapName.toPython() == norm_surah_name or row.chapName.toPython() == orig_surah_name:
      #     g.add((row.verse, qn.IsPartOf, row.chapter))
      #     g.add((row.chapter, RDFS.label, row.chapName))
      #     g.add((q_dua, qn.IsPartOf, row.verse))

          # print("Added triple: ", q_dua, qn.IsPartOf, row.verse)


def find_add_quran_ref(q_dua, surah_index, complete_ref, norm_surah_name, orig_surah_name):

  verse_index = int(re.sub('[^0-9]+', '', complete_ref))
  # print("Verse index = ", verse_index)
  # verse_index = Literal(verse_index, datatype = XSD.nonNegativeInteger)
  
  # qres = g.query(
  #   """
  #   PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
  #   PREFIX qo:<http://quranontology.com/Resource/>

  #   SELECT ?verse ?object WHERE
  #   {
  #     ?verse a qo:Verse.
  #     ?verse qo:VerseIndex ?object.
  #     filter (?object = ?verse_index)
  #   }
  #   """
  #   )


##############################################################

  # qres = g_Quran.query(
  #   """
  #   PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
  #   PREFIX qo:<http://quranontology.com/Resource/>
    
  #   # WITH <http://quranontology.com/Resource/>
  #   SELECT ?verse ?object WHERE
  #   {
  #     ?verse a qo:Verse.  
  #     ?verse qo:VerseIndex ?object.
  #   }
  #   """
  #   )
  # print("Verse literal = ", verse_index_lit, "for verse index = ", verse_index)



  # qres = g_Quran.query(
  #   """
  #   PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
  #   PREFIX qo:<http://quranontology.com/Resource/>

  #   SELECT ?verse ?object WHERE
  #   {
  #     ?verse a qo:Verse.
  #     ?verse qo:VerseIndex ?object.
  #     filter (?object = ?verse_index_lit)
  #   }
  #   """
  #   )

  qres = g_Quran.query(
    """
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX qo:<http://quranontology.com/Resource/>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?verse ?chapter ?vIndex ?chapIndex ?chapName WHERE
    {
      ?verse a qo:Verse.
      ?verse qo:VerseIndex ?vIndex.
      ?verse qo:IsPartOf ?chapter.
      ?chapter qo:ChpaterIndex ?chapIndex.
      ?chapter rdfs:label ?chapName. 
    }
    """
  )

  itr = 0
  for row in qres:
    # print(row)
    if row.vIndex.toPython() == verse_index:
      if row.chapName.toPython() == norm_surah_name or row.chapName.toPython() == orig_surah_name:
        g.add((row.verse, qn.IsPartOf, row.chapter))
        g.add((row.chapter, RDFS.label, row.chapName))
        g.add((row.chapter, qn.ChapterIndex, row.chapIndex))
        g.add((q_dua, qn.IsPartOf, row.verse))

        print("Added triple: ", q_dua, qn.IsPartOf, row.verse)



##############################################################


#   sparql = SPARQLWrapper("http://www.quranontology.com/Sparql")

#   sparql.setReturnFormat(JSON)
#   sparql.setQuery(
#     """
#     PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
#     PREFIX qo:<http://quranontology.com/Resource/>

#     SELECT ?verse WHERE
#     {
#       ?verse a qo:Verse.
#       ?verse qo:VerseIndex ?objectt.
#       filter (?object = ?verse_index)
#     }

#     """ % (verse_index)
#   )

#   try:
#       ret = sparql.queryAndConvert()

#       for r in ret["results"]["bindings"]:
#           print(r)
#   except Exception as e:
#       print(e)

##############################################################


#   # sparql_quran = SPARQLWrapper("http://www.quranontology.com/Sparql")
  # query(
  #   """
  #   PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
  #   PREFIX qo:<http://quranontology.com/Resource/>

  #   SELECT ?verse WHERE
  #   {
  #     ?verse a qo:Verse.
  #     ?verse qo:VerseIndex ?verse_index.
  #     filter (?verse_index = %s)
  #   }

  #   """ % (verse_index)
  # )
  # sparql.setQuery(query)

  # sparql.setReturnFormat(JSON)
  # results = sparql.query().convert()
  # print("verses:\n")
  # print(results)


##############################################################

  # g.add((q_dua, n.IsPartOf, ))
  

  # qres = g.query(
  #   """
  #     PREFIX qo:<http://quranontology.com/Resource/>
  #     PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
  #     SELECT ?s ?surah_name WHERE {
  #     ?s a :Chapter.
  #     ?s rdfs:label ?surah_name.
  #     ?s :ChapterIndex surah_index.
  #   }""")
  # print("Query results: \n")
  # for row in qres:
  #   print(row)
    

  # return surah_resource
##############################################################

# Hadith linking
##############################################################

# def link_hadith_duas(file_name):
#   # for all ahadith found in Sahih Bukhari, link hadith dua to it
#   with open(file_name, 'r') as file:
#     csvreader = csv.DictReader(file)
#     for row in csvreader:
#         if row["Dua_IRI"]:
#           print("dua", row["dua_id"], " belongs to:", row["Dua_IRI"])
#           find_add_hadith_ref()
#           # dua = URIRef(str(n)+"Dua-"+str(row["duaId"])) 
#           # g.add((dua, RDF.type, n.HadithDua))



#         # means Sahih Bukahri hadith is present
#           continue

        



##############################################################




# Quran linking
##############################################################

def add_Categories(file_name):
  # Make categories first: Read dua_category_map-v80.csv
  with open(file_name, 'r') as file:
    csvreader = csv.DictReader(file)
    # print(csvreader)

    count = 0
    for row in csvreader:
      cat = URIRef(str(n)+ "Category-"+str(row["category"]))
      g.add((cat, RDF.type, n.Category))
      
      g.add((cat, n.categoryId, Literal(row["id"], datatype=XSD.nonNegativeInteger)))
      g.add((cat, n.categoryUrduTitle, Literal(row["title_ur"], datatype = XSD.string)))
      g.add((cat, n.categoryEnglishTitle, Literal(row["title_en"], datatype = XSD.string)))

def add_duas(file_name):
  count = 0
  with open(file_name, 'r') as file:
    csvreader = csv.DictReader(file)
    with open('dua_modified.csv', 'r') as file2:
      csvreader2 = csv.DictReader(file2)
      for row in csvreader:
        if row["duaArabic"] != "Sample":
            dua = URIRef(str(n)+"Dua-"+str(row["duaId"]))
            g.add((dua, RDF.type, n.Dua))

            g.add((dua, n.duaId, Literal(row["dua_id"], datatype = XSD.nonNegativeInteger)))
            g.add((dua, n.duaUrduTitle, Literal(row["duaTitle_ur"], datatype = XSD.string)))
            g.add((dua, n.duaEnglishTitle, Literal(row["duaTitle_en"], datatype = XSD.string)))
            
            g.add((dua, n.duaArabicText, Literal(row["duaArabic"], datatype = XSD.string)))
            g.add((dua, n.duaEnglishText, Literal(row["dua_en"], datatype = XSD.string)))
            g.add((dua, n.duaUrduText, Literal(row["dua_ur"], datatype = XSD.string)))

            if row["duaType_en"] == "Qurani Dua":
                g.add((dua, RDF.type, n.QuranicDua))
                g.add((dua, n.duaType, Literal("Qurani Dua", datatype = XSD.string)))
                
                surah_index = 1
                for s in q_surah_lis:
                  if row["duaReference_ur"].find('-') == -1:
                  # not considering verse ranges for now

                    tokenized_csv_ref = tokenize(row["duaReference_ur"], conditions=is_arabicrange, morphs=strip_tashkeel)
                    normalized_csv_ref = normalizeArabic(deNoise(row["duaReference_ur"]))
                    tokenized_surah = tokenize(s[0], conditions=is_arabicrange, morphs=strip_tashkeel)
                    normalized_surah = normalizeArabic(deNoise(s[0]))                
                    csv_ref_arabic = re.sub('[0-9 ()]+', '', normalizeArabic(deNoise(row["duaReference_ur"])))
                    if normalized_csv_ref.find(normalized_surah) != -1 and abs(len(csv_ref_arabic)-len(normalized_surah)) <= 2:
                      print("same")
                      find_add_quran_ref(dua, surah_index, normalized_csv_ref, normalized_surah, s[0])

                      surah_index +=1
                      count+=1
                  else:
                    # considering verse ranges now, but not commas
                    if row["duaReference_ur"].find(',') == -1:

                      tokenized_csv_ref = tokenize(row["duaReference_ur"], conditions=is_arabicrange, morphs=strip_tashkeel)
                      normalized_csv_ref = normalizeArabic(deNoise(row["duaReference_ur"]))
                      ref_verse_range =  re.sub('[^0-9\-]', '', normalized_csv_ref)
                      verse_range_ends = ref_verse_range.split('-')
                      for i in range(len(verse_range_ends)):
                        verse_range_ends[i] = int(verse_range_ends[i])
                      # print("Verse range = ", verse_range_ends)

                      tokenized_surah = tokenize(s[0], conditions=is_arabicrange, morphs=strip_tashkeel)
                      normalized_surah = normalizeArabic(deNoise(s[0]))
                      # if len(tokenize(s[0], conditions=is_arabicrange, morphs=strip_tashkeel))<=2 and normalizeArabic(deNoise(row["duaReference_ur"])).find(normalizeArabic(deNoise(s[0]))) == 0 and (len(tokenize(s[0], conditions=is_arabicrange, morphs=strip_tashkeel)[0]) > len(normalizeArabic(deNoise(row["duaReference_ur"])))+1  or  len(tokenize(s[0], conditions=is_arabicrange, morphs=strip_tashkeel)[0]) +1 < len(normalizeArabic(deNoise(row["duaReference_ur"])))+1):
                      
                      csv_ref_arabic = re.sub('[0-9 ()]+', '', normalizeArabic(deNoise(row["duaReference_ur"])))
                      
                      if normalized_csv_ref.find(normalized_surah) != -1 and abs(len(csv_ref_arabic)-len(normalized_surah)) <= 2:
                        print("same")
                        for v in verse_range_ends:
                          pos = re.search(r"\d", normalized_csv_ref)
                          print(pos.start())
                          new_normalized_csv_ref = re.sub('[0123456789-]','',normalized_csv_ref)
                          new_normalized_csv_ref = new_normalized_csv_ref[:pos.start()] + str(v) + new_normalized_csv_ref[pos.start():]
                          print(new_normalized_csv_ref)
                          find_add_quran_ref(dua, surah_index, new_normalized_csv_ref, normalized_surah, s[0])
            else:
              g.add((dua, RDF.type, n.HadithDua))
              g.add((dua, n.duaType, Literal(row["duaType_en"], datatype = XSD.string)))
    
              for row2 in csvreader2:
                if row2["Dua_IRI"]:
                # print("dua", row2["dua_id"], " belongs to:", row2["Dua_IRI"])
                 find_add_hadith_ref(dua, row2["Dua_IRI"])


  print("Counts of found surahs = ", count)
####################################################################################



def main():
  add_Categories('Duaein Data - For KG - revisedCategories-v57.csv')
  add_duas('Duaein Data - For KG - duas-test-v80.csv')

  g.serialize(destination='Populated_Dua_KG.ttl', format='turtle')


main()
