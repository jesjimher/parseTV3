#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import re
from bs4 import BeautifulSoup
from lxml import etree as ET
import urllib2
import argparse

CANALS=["tv3cat","33","canalsuper3"]
BASEURL="http://www.tv3.cat/programacio"

parser=argparse.ArgumentParser(description="Descarrega la programació dels canals de TV de Catalunya en format XMLTV")
parser.add_argument('directori',help="Directori a on es generaran els fitxers")
parser.add_argument('-d','--dies',help="Nombre de dies a descarregar (per defecte 3)",type=int,default=3,required=False)
args=parser.parse_args()


# Llegeix de la web l'HTML del dia/canal especificat, i retorna un llista de programes
def explorar(canal,dia):
    url="/".join([BASEURL,dia.strftime("%Y%m%d"),canal])
    resp=urllib2.urlopen(url)
    html=resp.read()
    soup=BeautifulSoup(html)

    lprogs=soup.find_all("div",class_="emissio")
    epg=[]
    for pr in lprogs:
        # Mirar si és un programa simple o una agrupació de programes
        if pr.ul:
            # Si és un grup de programes, ignoram el grup i afegim els subprogrames
            for p in pr.find_all("li"):
                horatag=p.find("span",class_="hora")
                horatext=horatag.get_text().strip()
                hora=datetime.datetime.strptime(horatext,"%H:%M")
                diahora=datetime.datetime.combine(dia,hora.time())

                # El títol no està dins cap tag concret, simplement està a continuació de l'hora
                llista=list(horatag.parent.stripped_strings)[1:3]
                titol=llista[0]
                if len(llista)>1: subtitol=llista[1]

                d={'horaini':diahora,'title':titol}
                if p.textarea:
                    d['desc']=p.textarea.get_text().strip()
                if subtitol:
                    d['sub-title']=subtitol
        else:
            # Si no tenia ul és que és un programa simple
            hora=pr.find("span",class_="hora").get_text().strip()
            hora=datetime.datetime.strptime(hora,"%H:%M")
            diahora=datetime.datetime.combine(dia,hora.time())

            llista=pr.p.get_text().strip().splitlines()
            tit=llista[0]
            d={'horaini':diahora,'title':tit}
            if pr.textarea:
                d['desc']=pr.textarea.get_text().strip()
            if len(llista)>1: d['sub-title']=llista[1]
            epg.append(d)

    # Sumar un dia als programes que comencen més tard de mitjanit
    i=1
    while (i<len(epg)) and (epg[i]['horaini']>=epg[i-1]['horaini']): i+=1
    if i<len(epg):
        for j in range(i,len(epg)):
            epg[j]['horaini']+=datetime.timedelta(1)
#            print "Afegit un dia a %s %s" % (epg[j]['horaini'],epg[j]['title'])
    return epg


# Generar un arbre XML en format XMLTV a partir d'un dict amb programes classificats per canal
def generarXML(epg):
    # Crear l'arbre XML
    tv=ET.Element("tv",attrib={'source-info-url':BASEURL})

    # Afegir primer la llista de canals
    for c in epg.keys():
        aux=ET.SubElement(tv,"channel",attrib={'id':'C'+c+'.tv3.cat'})
        aux=ET.SubElement(aux,"display-name")
        aux.text=c

    # I després els programes
    for canal in epg:
        for prog in epg[canal]:
        #    print "Afegint %s" % prog['title']
            pr={}
            pr['channel']='C'+canal+'.tv3.cat'
            pr['start']=prog['horaini'].strftime("%Y%m%d%H%M%S")
            pr['stop']=prog['horafi'].strftime("%Y%m%d%H%M%S")
            p=ET.SubElement(tv,"programme",attrib=pr)
            aux=ET.SubElement(p,"title")
            aux.text=prog["title"]
            if 'sub-title' in prog:
                aux=ET.SubElement(p,"sub-title")
                aux.text=prog["sub-title"]
            if 'desc' in prog:
                aux=ET.SubElement(p,"desc")
                aux.text=re.sub(r'[\r]','\n',prog['desc'])
    return tv            

# Inicialitzar la epg de cada canal com una llista buida
epg={}
for c in CANALS:
    epg[c]=[]
# Llegir els programes de cada canal i dia, i afegir-los    
for canal in CANALS:
    for dia in range(args.dies):
        diaexpl=(datetime.datetime.now()+datetime.timedelta(dia))
        print "Descarregant programació de %s per a la data %s... " % (canal,diaexpl.strftime("%Y%m%d")),
        progsavui=explorar(canal,diaexpl)
        print "Llegits %d programes" % len(progsavui)
        epg[canal]+=progsavui

# TODO: Juntar Super3 i 33, són el mateix canal a diferents hores

# Calcular l'hora final de cada espai posant la d'inici del següent programa (si és el darrer posam 1h)
for c in CANALS:
    for i in range(len(epg[c])):
        if i<len(epg[c])-1:
            epg[c][i]['horafi']=epg[c][i+1]['horaini']
        else:
            epg[c][i]['horafi']=epg[c][i]['horaini']+datetime.timedelta(hours=1)

tv=generarXML(epg)
#nomfich=avui+"_"+canal+".xmltv"
rang=datetime.datetime.now().strftime("%Y%m%d")+"-"+(datetime.datetime.now()+datetime.timedelta(args.dies-1)).strftime("%Y%m%d")
nomfich="programacio_"+rang+".xmltv"
ruta=os.path.join(args.directori,nomfich)
with open(ruta,"w") as f:
    print "Creant fitxer %s" % ruta
    f.write(ET.tostring(tv,encoding="utf-8",pretty_print=True,xml_declaration=True))

