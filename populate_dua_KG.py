from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import FOAF, XMLNS, XSD, RDF, RDFS, OWL
import csv

g = Graph()
g.parse('dua_ontology_final_copy.ttl', format = 'turtle')
n = Namespace('http://www.semanticweb.org/szm/dua-ontology#')

# Make categories first: Read dua_category_map-v80.csv
with open('Duaein Data - For KG - revisedCategories-v57.csv', 'r') as file:
  csvreader = csv.DictReader(file)
  # print(csvreader)

  count = 0
  for row in csvreader:
    cat = URIRef(str(n)+ "Category-"+str(row["category"]))
    g.add((cat, RDF.type, n.Category))
    
    g.add((cat, n.categoryId, Literal(row["id"], datatype=XSD.nonNegativeInteger)))
    g.add((cat, n.categoryUrduTitle, Literal(row["title_ur"], datatype = XSD.string)))
    g.add((cat, n.categoryEnglishTitle, Literal(row["title_en"], datatype = XSD.string)))


with open('Duaein Data - For KG - duas-test-v80.csv', 'r', 'utf-8') as file:
  csvreader = csv.DictReader(file)
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
        else:
            g.add((dua, RDF.type, n.HadithDua))
            g.add((dua, n.duaType, Literal(row["duaType_en"], datatype = XSD.string)))
    

  g.serialize(destination='Populated_Dua_KG.ttl', format='turtle')


# DuaCategory
