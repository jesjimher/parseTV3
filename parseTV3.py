#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import re
from bs4 import BeautifulSoup
from lxml import etree as ET
import urllib2

CANALS=["tv3cat","33","canalsuper3"]
#CANALS=["tv3cat","33"]
BASEURL="http://www.tv3.cat/programacio"
NDIES=2


for canal in CANALS:
    for dia in range(NDIES):
        avui=(datetime.datetime.now()+datetime.timedelta(dia)).strftime("%Y%m%d")
        url="/".join([BASEURL,avui,canal])
        print "Descarregant programació de %s per a la data %s... " % (canal,avui),
        resp=urllib2.urlopen(url)
        html=resp.read()
        soup=BeautifulSoup(html)

        dia=datetime.datetime.today()
        lprogs=soup.find_all("div",class_="emissio")
        epg=[]
        cont=0
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
                    # Assumim que sempre hi ha subtítol, si no és així donarà problemes
                    llista=list(horatag.parent.stripped_strings)[1:3]
                    titol=llista[0]
                    subtitol=llista[1]

                    d={'hora':diahora,'title':titol}
                    if p.textarea:
                        d['desc']=p.textarea.get_text().strip()
                    if subtitol:
                        d['sub-title']=subtitol
                    cont+=1
            else:
                # Si no tenia ul és que és un programa simple
                hora=pr.find("span",class_="hora").get_text().strip()
                hora=datetime.datetime.strptime(hora,"%H:%M")
                diahora=datetime.datetime.combine(dia,hora.time())

                llista=pr.p.get_text().strip().splitlines()
                tit=llista[0]
                d={'hora':diahora,'title':tit}
                if pr.textarea:
                    d['desc']=pr.textarea.get_text().strip()
                if len(llista)>1: d['sub-title']=llista[1]
                epg.append(d)
                cont+=1

        print "Llegits %d programes" % cont

        # Sumar un dia als programes que comencen més tard de mitjanit
        i=1
        while (i<len(epg)) and (epg[i]['hora']>=epg[i-1]['hora']):
            i+=1
        if i<len(epg):
            for j in range(i,len(epg)):
                epg[j]['hora']+=datetime.timedelta(1)
    #            print "Afegit un dia a %s %s" % (epg[j]['hora'],epg[j]['title'])

        # Crear l'arbre XML
        tv=ET.Element("tv",attrib={'source-info-url':url})

        # Afegir la llista de canals
        ch={'id':'C'+canal,'display-name':canal}
        aux=ET.SubElement(tv,"channel",attrib={'id':ch['id']})
        aux=ET.SubElement(aux,"display-name")
        aux.text=ch['display-name']

        # I després els programes
        for prog in epg:
        #    print "Afegint %s" % prog['title']
            pr={}
            pr['channel']=ch['id']
            pr['start']=prog['hora'].strftime("%Y%m%d%H%M")
            p=ET.SubElement(tv,"programme",attrib=pr)
            aux=ET.SubElement(p,"title")
            aux.text=prog["title"]
            if 'sub-title' in prog:
                aux=ET.SubElement(p,"sub-title")
                aux.text=prog["sub-title"]
            if 'desc' in prog:
                aux=ET.SubElement(p,"desc")
                aux.text=re.sub(r'[\r]','\n',prog['desc'])
        nomfich=avui+"_"+canal+".xmltv"
        with open(nomfich,"w") as f:
            print "Creant fitxer %s" % nomfich
            f.write(ET.tostring(tv,encoding="utf-8",pretty_print=True,xml_declaration=True))

