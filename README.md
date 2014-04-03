parseTV3
========

Petit script que permet descarregar-se la programació dels diferents canals de Televisió de Catalunya en format XMLTV, el format estàndard reconegut per qualsevol media center mínimament decent, com ara TVHeadend, MythTV, MediaPortal o semblants.

La invocació és molt senzilla, basta executar:

parseTV3 .

Es generarà al directori actual un fitxer XMLTV per a cada canal i dia. Si no s'indica una altra cosa amb el paràmetre -d, es descarreguen 3 dies de programació a partir de la data actual. 

Per defecte es descarrega la informació de TV3 Cat, 33 i Canal Super 3. Es poden afegir/eliminar canals modificant la variable de configuració CANALS que es troba al principi del fitxer. Els identificadors són els que apareixen al final de la URL de la web de TV3 quan consultam la programació. Per exemple, si consultam la programació de TV3 HD pel 3 d'abril, la URL és http://www.tv3.cat/programacio/20140403/3hd, de manera que l'identificador seria "3hd".

Per acabar, no tenc molt clara la legalitat d'extreure i manipular aquest tipus d'informació des de la web de TVC. De totes formes, i tenint en compte que es tracta de canals públics i no hi ha interés lucratiu (només vull tenir informació de la programació al meu media center) no veig per què hauria d'haver-hi cap problema. En qualsevol cas, recoman que es faci un ús responsable de l'eina i, per exemple, no es consulti la programació massa sovint (amb una vegada al dia hi ha més que suficient). No cal dir que no em faig responsable de cap ús negatiu/fraudulent/dolent en general que es faci d'aquest programa, així com tampoc de cap dany que aquest pugui causar. La idea és que funcioni bé, i jo sóc el primer interessat en què sigui així (el faig servir a diari), però no puc donar cap tipus de garantia.
