# -*- coding: utf-8 -*-
"""Autores de la colección: los que tienen nombre propio.

Buena parte de las piezas no tiene autor conocido —los relieves de Nínive, las tablillas
de Uruk, la máscara de Micenas, los frescos de Dura Europos— y esas NO aparecen aquí: la
sección de autores solo reúne aquello de lo que sabemos quién lo hizo.

`patron` es lo que aparece en el campo `artist` de las fichas una vez quitada la fecha
entre paréntesis; de ahí se deduce qué obras de la colección son de cada uno, sin listas
escritas a mano que se queden obsoletas.
"""

AUTORES = [
{
 "clave": "miguel_angel", "nombre": "Miguel Ángel Buonarroti", "anios": "1475–1564",
 "oficio": "Escultor, pintor y arquitecto florentino",
 "patron": ["Miguel Ángel Buonarroti"],
 "bio": "Nacido en Caprese el 6 de marzo de 1475, entró a los trece años en el taller de Domenico Ghirlandaio y tuvo por protector a Lorenzo de' Medici. Se tenía por escultor antes que pintor. En 1505 Julio II le encargó su tumba monumental; recortados los fondos, el papa lo puso a pintar la bóveda de la Sixtina. Firmó el contrato el 8 de mayo de 1508 y la terminó en 1512; trabajó de pie sobre un andamio, con el cuello doblado hacia atrás, no tumbado. Nueve escenas del Génesis, profetas, sibilas y desnudos se ordenan dentro de una arquitectura pintada. Murió en Roma el 18 de febrero de 1564.",
},
{
 "clave": "masaccio", "nombre": "Masaccio", "anios": "1401–c. 1428",
 "oficio": "Pintor florentino",
 "patron": ["Masaccio"],
 "bio": "Masaccio nació el 21 de diciembre de 1401 en Castel San Giovanni, hoy San Giovanni Valdarno. En enero de 1422 ya figuraba como «pictor» en el gremio florentino de Medici e Speziali. En 1426 pintó el políptico del Carmine de Pisa, cuya tabla central está en la National Gallery. Trabajó «codo con codo» con Masolino en la capilla Brancacci, y tuvo a Brunelleschi por maestro de perspectiva en la Trinidad de Santa Maria Novella. Sus figuras pesan y reciben la luz de una sola fuente. Murió en Roma hacia 1428, antes del 18 de noviembre de 1429. Vasari enumera a quienes estudiaron la Brancacci, de Leonardo a Miguel Ángel.",
},
{
 "clave": "tiziano", "nombre": "Tiziano Vecellio", "anios": "c. 1488–1576",
 "oficio": "Pintor veneciano",
 "patron": ["Tiziano Vecellio"],
 "bio": "Nació en Pieve di Cadore hacia 1488-1490, fecha aún discutida. Se formó con Gentile y Giovanni Bellini y hacia 1507 se asoció con Giorgione. Carlos V, que lo retrató en Bolonia, lo ennobleció en 1533; Tiziano viajó a Roma en 1545-1546 y a la corte imperial de Augsburgo en 1548 y 1550-1551. Después trabajó sobre todo para los Austrias, con Felipe II como su mecenas más constante, y por eso el Prado guarda la colección más extensa de su obra. Vasari escribió, elogiándolos, que sus cuadros tardíos de cerca no se reconocían y de lejos parecían perfectos. Murió en Venecia el 27 de agosto de 1576, de fiebre, durante una epidemia de peste.",
},
{
 "clave": "bruegel", "nombre": "Pieter Bruegel el Viejo", "anios": "c. 1525–1569",
 "oficio": "Pintor y grabador flamenco",
 "patron": ["Pieter Bruegel el Viejo"],
 "bio": "Se formó, según Karel van Mander, con Pieter Coecke van Aelst, con cuya hija Mayken se casó en Bruselas en 1563. En 1551 ingresó como maestro en el gremio de San Lucas de Amberes. En 1552-1553 recorrió Italia hasta Sicilia y vivió en Roma, y los dibujos de los Alpes que hizo en ese viaje nutrieron grabados para el editor Hieronymus Cock. Sus últimas obras, lejos de ignorar Italia, muestran una marcada afinidad con el arte italiano. Pintó sobre todo para coleccionistas: Niclaes Jonghelinck tenía dieciséis cuadros suyos en 1566. Su hijo Pieter el Joven y su hermano Jan montaron un taller de réplicas de sus composiciones muy demandadas en Flandes.",
},
{
 "clave": "cormon", "nombre": "Fernand Cormon", "anios": "1845–1924",
 "oficio": "Pintor francés",
 "patron": ["Fernand Cormon"],
 "bio": "Fernand-Anne Piestre, llamado Cormon, nació y murió en París (1845–1924). Pintor de historia y de temas religiosos de factura académica y muralista, hizo carrera oficial bajo la Tercera República: medallas en el Salón desde 1870 y encargos públicos. Su Caín (1880, Musée d'Orsay), de 4 × 7 metros e inspirado en «La Conciencia» de Victor Hugo, lo compró el Estado, le valió la Legión de Honor e inauguró su especialidad prehistórica, pintada con modelos vivos vestidos de pieles. Por su atelier libre pasaron Émile Bernard (1884–1886), Toulouse-Lautrec y, de marzo a junio de 1886, Van Gogh. Aquellos alumnos desafiaban sus principios académicos; tras un enfrentamiento en abril de 1886, Cormon cerró temporalmente el taller.",
},
{
 "clave": "blake", "nombre": "William Blake", "anios": "1757–1827",
 "oficio": "Poeta, grabador y pintor inglés",
 "patron": ["William Blake"],
 "bio": "Nacido en Londres el 28 de noviembre de 1757, atribuyó a una visión de su hermano Robert, muerto en 1787, el secreto de su «Illuminated Printing»: texto e imagen trazados sobre el cobre con un líquido resistente al ácido. El método le permitió ser a la vez cajista, impresor, encuadernador y vendedor de su poesía; Catherine Boucher, con quien casó en 1782, le ayudaba a colorear e imprimir, y no hay dos ejemplares iguales. Tras el fracaso de su exposición de 1809 se hundió en la pobreza; sus últimos años, gracias a John Linnell, fueron más cómodos. En su mitología, Urizen encarna la razón. Murió en Londres el 12 de agosto de 1827.",
},
{
 "clave": "turner", "nombre": "J. M. W. Turner", "anios": "1775–1851",
 "oficio": "Pintor y acuarelista inglés",
 "patron": ["J.M.W. Turner"],
 "bio": "Joseph Mallord William Turner nació el 23 de abril de 1775 en Maiden Lane, Covent Garden, hijo de un barbero. Entró en las escuelas de la Royal Academy en diciembre de 1789, con catorce años, y fue académico en 1802. La crítica acusó su obra tardía de «extravagancia y exageración» y la comparó con ensalada de langosta o espuma de jabón; Ruskin la defendió desde 1843. En 1846 se instaló con Sophia Booth en Davis Place, Chelsea, y dio en llamarse «almirante Booth». Murió en Chelsea el 19 de diciembre de 1851. Su legado a la nación, fijado en 1856, reúne casi trescientos óleos y unas treinta mil obras sobre papel.",
},
{
 "clave": "dore", "nombre": "Gustave Doré", "anios": "1832–1883",
 "oficio": "Ilustrador, grabador y pintor francés",
 "patron": ["Gustave Doré"],
 "bio": "Nació en Estrasburgo el 6 de enero de 1832 y murió en París el 23 de enero de 1883. De 1848 a 1851 dibujó caricaturas semanales para el Journal pour rire. Su fama se debe al libro ilustrado con grabado en madera: con más de cuarenta grabadores produjo más de noventa libros, entre ellos el Infierno de Dante (1861), el Quijote y los Cuentos de Perrault (1862), la Biblia y El paraíso perdido (1865). En 1872 empezó a retratar los barrios pobres de Londres. El Museo de Orsay le da un lugar en el imaginario colectivo. Después de 1870 se dedicó sobre todo a pintar y esculpir, con menos reconocimiento.",
},
{
 "clave": "scorel", "nombre": "Jan van Scorel", "anios": "1495–1562",
 "oficio": "Pintor neerlandés",
 "patron": ["Jan van Scorel"],
 "bio": "Hacia 1517 trabajaba en Utrecht con Jan Gossaert. En 1519 pasó por Núremberg, donde conoció a Durero, y desde Venecia se embarcó en peregrinación a Tierra Santa. En Roma lo protegió Adriano VI, papa nacido en Utrecht, que en 1522 lo nombró conservador de la colección pontificia del Belvedere. Tras la muerte del papa en 1523 volvió a Utrecht, donde fue canónigo del capítulo de Santa María. Allí introdujo en la pintura holandesa desnudos, arquitecturas clásicas y paisajes imaginarios a la italiana. Sus retratos colectivos de peregrinos de Jerusalén están en el origen del retrato de grupo holandés. Fue también arquitecto y técnico hidráulico, y maestro de Maarten van Heemskerck y Antonis Mor.",
},
{
 "clave": "watts", "nombre": "George Frederic Watts", "anios": "1817–1904",
 "oficio": "Pintor y escultor inglés",
 "patron": ["George Frederic Watts"],
 "bio": "George Frederic Watts nació en Londres el 23 de febrero de 1817 y murió el 1 de julio de 1904. En Italia (1843–1847) estudió a los venecianos del siglo XVI, de quienes tomó su colorido cálido. Pintó alegorías como La esperanza (1885) para «sugerir grandes pensamientos que apelen a la imaginación y al corazón». Rechazó dos veces un título de baronet (1885 y 1894) y en 1902 entró en la recién creada Orden del Mérito. Desde 1883 donó a la National Portrait Gallery sus retratos del «Hall of Fame»; su regalo a la nación nutrió también la Tate. Su galería de Compton la diseñó, por encargo suyo, el arquitecto local Christopher Hatton Turnor.",
},
{
 "clave": "danby", "nombre": "Francis Danby", "anios": "1793–1861",
 "oficio": "Pintor irlandés",
 "patron": ["Francis Danby"],
 "bio": "Nacido el 16 de noviembre de 1793 en Common, Killinick (condado de Wexford), estudió en la escuela de dibujo de la Dublin Society. En 1813 fue a pie de Londres a Bristol, donde llegó a ser el miembro más conocido de la escuela local. Instalado en Londres desde 1824, acusó a John Martin de plagiar su Apertura del sexto sello, que en la Royal Academy de 1828 atrajo tales multitudes que hubo que cambiarla de sala. En 1829, acosado por acreedores y separado de su mujer, huyó al continente con su amante Ellen Evans, y vivió entre Brujas, Suiza y París. Volvió en 1839 y murió en Exmouth el 10 de febrero de 1861.",
},
{
 "clave": "cole", "nombre": "Thomas Cole", "anios": "1801–1848",
 "oficio": "Pintor angloamericano",
 "patron": ["Thomas Cole"],
 "bio": "Thomas Cole nació el 1 de febrero de 1801 en Bolton, Lancashire, y emigró con su familia a Estados Unidos en 1818. Fue retratista itinerante en Filadelfia, Ohio y Pittsburgh. Se le atribuye el arranque de la Escuela del Río Hudson, primer gran movimiento artístico estadounidense. Viajó por Europa entre 1829 y 1832. Para el comerciante Luman Reed pintó en 1835–1836 «El curso del imperio», y en 1839–1840 «El viaje de la vida»: ciclos alegóricos donde el paisaje sigue siendo protagonista. Denunció el daño de la industria y el ferrocarril a los Catskill. Murió de pleuresía en Catskill (Nueva York) el 11 de febrero de 1848.",
},
{
 "clave": "cranach", "nombre": "Lucas Cranach el Viejo", "anios": "1472–1553",
 "oficio": "Pintor y grabador alemán",
 "patron": ["Lucas Cranach el Viejo"],
 "bio": "Nació probablemente en 1472 en Kronach, de donde tomó el apellido. Sus primeras obras conocidas son de Viena, hacia 1502. En 1505 llegó a Wittenberg como pintor de corte de Federico el Sabio y sirvió a tres electores sucesivos. Obtuvo en 1520 el privilegio de una botica, imprimió en su casa textos de la Reforma y parte de la Biblia de Lutero, y fue burgomaestre varias veces. Fue padrino en la boda de Lutero y luego de un hijo suyo, y difundió su retrato. Su taller estandarizó el trabajo para delegarlo: salieron de él más de cincuenta versiones de Adán y Eva. Murió en Weimar el 16 de octubre de 1553.",
},
{
 "clave": "durero", "nombre": "Alberto Durero", "anios": "1471–1528",
 "oficio": "Pintor, grabador y teórico alemán",
 "patron": ["Alberto Durero"],
 "bio": "Hijo segundo del orfebre Albrecht Dürer el Viejo, emigrado de Hungría a Núremberg en 1455, se formó en el taller paterno y desde 1486 con el pintor Michael Wolgemut. Viajó a Italia en 1494-1495 y en 1505-1507. Hacia 1496 sustituyó su primera sigla por el monograma que lo identificaría. Llevó el grabado a la categoría de arte independiente. Según la tradición, demandó a Marcantonio Raimondi por copiar sus grabados, uno de los primeros pleitos documentados sobre propiedad intelectual. En sus últimos años escribió sobre geometría y perspectiva (1525), fortificación (1527) y proporción humana (1528). Trabajó para los emperadores Maximiliano I y Carlos V.",
},
{
 "clave": "caravaggio", "nombre": "Caravaggio", "anios": "1571–1610",
 "oficio": "Pintor lombardo",
 "patron": ["Caravaggio"],
 "bio": "Michelangelo Merisi nació en Milán, probablemente el 25 de septiembre de 1571, y fue bautizado allí el 30; Caravaggio era el pueblo de origen de su familia. Aprendiz de Simone Peterzano desde 1584, hacia 1592 llegó a Roma, donde pintó flores y frutas para el Cavalier d'Arpino. En 1599 recibió las historias de san Mateo de la capilla Contarelli. Pintaba directamente sobre el lienzo, con muy poca preparación, y usaba como modelos a gente corriente. En 1606 mató a Ranuccio Tomassoni en una riña y huyó de Roma a Nápoles, Malta y Sicilia. Buscando el perdón papal, murió en Porto Ercole el 18 de julio de 1610, quizá de malaria.",
},
{
 "clave": "rembrandt", "nombre": "Rembrandt van Rijn", "anios": "1606–1669",
 "oficio": "Pintor y grabador neerlandés",
 "patron": ["Rembrandt van Rijn", "Rembrandt van Rijn y taller"],
 "bio": "Nacido en Leiden el 15 de julio de 1606, hijo de un molinero, se formó con Jacob van Swanenburgh y, durante seis meses, con Pieter Lastman en Ámsterdam. Sus aguafuertes le dieron fama internacional en vida. Cerca de una décima parte de su obra pintada y grabada son estudios de su propio rostro y autorretratos, que en el Rijksmuseum van de hacia 1628 a 1661. Endeudado por la casa comprada en 1639 y por su colección, quebró en 1656; el inventario de sus bienes levantado ese año documenta su alcance. Murió en Ámsterdam el 4 de octubre de 1669 y fue enterrado en la Westerkerk.",
},
{
 "clave": "rubliov", "nombre": "Andréi Rubliov", "anios": "c. 1360–1430",
 "oficio": "Monje e iconógrafo ruso",
 "patron": ["Andréi Rubliov"],
 "bio": "Andréi Rubliov nació entre 1360 y 1370 y murió en Moscú en 1430. Monje vinculado al monasterio de la Trinidad de san Sergio de Rádonezh, pasó su madurez en el de Andrónikov, en Moscú, hoy museo dedicado a él. En 1405 trabajó con Teófanes el Griego en la catedral de la Anunciación, y en 1408, con el monje Daniil, en la Dormición de Vladímir. La Trinidad, pintada para la tumba de san Sergio hacia 1411 o en la década de 1420, fue fijada en 1551 por el concilio de los Cien Capítulos como modelo a pintar «como Andréi Rubliov». La Iglesia ortodoxa rusa lo canonizó en 1988.",
},
{
 "clave": "delacroix", "nombre": "Eugène Delacroix", "anios": "1798–1863",
 "oficio": "Pintor francés",
 "patron": ["Eugène Delacroix"],
 "bio": "Nació en Charenton-Saint-Maurice el 26 de abril de 1798 y murió en París el 13 de agosto de 1863. Fue alumno de Pierre-Narcisse Guérin, en cuyo taller conoció a Géricault. El Salón de 1827 lo presentó como cabeza de la corriente romántica frente a Ingres, cabeza de la clasicista. De enero a julio de 1832 recorrió Marruecos, Argelia y España con la misión diplomática del conde de Mornay, y sus apuntes le dieron temas hasta el final. Decoró el Palais-Bourbon, el Luxemburgo, la Galería de Apolo del Louvre y una capilla de Saint-Sulpice. Su Diario, publicado en 1893-1895, está entre los cuadernos de artista más penetrantes desde Leonardo.",
},
{
 "clave": "gauguin", "nombre": "Paul Gauguin", "anios": "1848–1903",
 "oficio": "Pintor francés",
 "patron": ["Paul Gauguin"],
 "bio": "Tras seis años en la marina mercante, su tutor Gustave Arosa le consiguió un puesto de agente de bolsa; empezó a pintar con Pissarro. Expuso con los impresionistas desde 1880 y perdió el empleo con el crac bursátil de 1882. En Pont-Aven, en Bretaña, llegó en 1888 con La visión después del sermón a los planos de color y los contornos marcados que llamó «sintetismo», y en 1891 el crítico Albert Aurier lo proclamó jefe de los simbolistas. Buscó en Tahití (1891) una cultura que creía ajena a los males de la civilización moderna. En 1901 se retiró a Hiva Oa, en las Marquesas, donde murió solo, enfermo de sífilis y con un pleito pendiente.",
},
{
 "clave": "corot", "nombre": "Camille Corot", "anios": "1796–1875",
 "oficio": "Pintor francés",
 "patron": ["Jean-Baptiste-Camille Corot"],
 "bio": "Jean-Baptiste-Camille Corot nació en París en julio de 1796 y murió en la misma ciudad en 1875. Se formó con los paisajistas clasicistas Michallon y Bertin, pero pintó también del natural en Fontainebleau. El viaje a Italia de 1825–1828 fue decisivo; volvió en 1834 y 1843. En invierno componía en el taller paisajes mitológicos y religiosos para el Salón; sus estudios al óleo se aprecian hoy tanto como sus cuadros acabados, y su tratamiento de la luz influyó en los impresionistas. Ayudó a Daumier, ciego, y a la viuda de Millet, y firmaba, apenas retocadas, obras de sus alumnos, origen de falsificaciones y de problemas de atribución.",
},
{
 "clave": "velazquez", "nombre": "Diego Velázquez", "anios": "1599–1660",
 "oficio": "Pintor sevillano",
 "patron": ["Diego Velázquez"],
 "bio": "Bautizado en Sevilla el 6 de junio de 1599, pasó unos meses con Francisco de Herrera el Viejo y en 1611 firmó contrato de aprendizaje con Francisco Pacheco, luego su suegro. A los veinticuatro años se trasladó a Madrid; tras retratar a Felipe IV, el rey lo nombró pintor de cámara, primero de muchos cargos palatinos, algunos con pesadas tareas administrativas. Solo salió de España dos veces, ambas a Italia: en 1629, a estudiar, y en 1649, a comprar pinturas y esculturas para el rey. En sus últimas obras las pinceladas, que de cerca parecen incoherentes, resultan exactas a la distancia debida. Murió en Madrid el 6 de agosto de 1660.",
},
{
 "clave": "john_martin", "nombre": "John Martin", "anios": "1789–1854",
 "oficio": "Pintor y grabador inglés",
 "patron": ["John Martin"],
 "bio": "John Martin nació en julio de 1789 en Haydon Bridge, Northumberland, y murió en 1854 en Douglas, isla de Man. Se formó en Newcastle y estudió arquitectura y perspectiva en Londres. Pintó catástrofes pobladas de figuras diminutas y arquitecturas fantásticas, como «El Diluvio» (1834). Sus mezzotintas asequibles para la Biblia y el «Paraíso perdido» colgaron en casas de todo el mundo, y más de cinco mil personas pagaron por ver «El festín de Baltasar» en 1821. La Royal Academy nunca lo eligió; Constable lo llamó «pintor de pantomimas». Desde finales de la década de 1820 publicó planes de alcantarillado, malecón y ferrocarril para Londres que nunca se hicieron como él quería.",
},
{
 "clave": "bosco", "nombre": "El Bosco", "anios": "c. 1450–1516",
 "oficio": "Pintor brabanzón",
 "patron": ["Hieronymus Bosch, El Bosco"],
 "bio": "Jheronimus van Aken nació hacia 1450 en ’s-Hertogenbosch, aunque no consta el año. Hijo y nieto de pintores, aparece documentado desde 1474 y en 1486 ingresó en la cofradía de Nuestra Señora de su ciudad. Firmaba «Jheronimus Bosch», nombre tomado de su lugar de residencia, y Felipe el Hermoso le encargó un Juicio Final. De las 35 a 40 pinturas que se le atribuyen solo siete están firmadas y ninguna fechada, de modo que su cronología es insegura. Fue enterrado en su ciudad el 9 de agosto de 1516. Felipe II lo apreció mucho, y por eso la colección más importante de su obra está en el Prado.",
},
{
 "clave": "rubens", "nombre": "Peter Paul Rubens", "anios": "1577–1640",
 "oficio": "Pintor flamenco",
 "patron": ["Peter Paul Rubens"],
 "bio": "Nació en Siegen, adonde había huido su padre calvinista, y se formó con Tobias Verhaecht, Adam van Noort y Otto van Veen. Entre 1600 y 1608 trabajó en Italia al servicio del duque de Mantua. De vuelta en Amberes fue pintor de corte de los archiduques Alberto e Isabel y levantó el taller de pintor más famoso de Europa: él pintaba el boceto al óleo y los ayudantes, como el joven Van Dyck, ejecutaban el cuadro grande. Como agente de la infanta Isabel negoció la paz de 1630 entre España e Inglaterra. Lo armaron caballero Carlos I de Inglaterra y, en 1631, Felipe IV: único pintor así honrado por ambos reyes. Hablaba seis lenguas.",
},
{
 "clave": "poussin", "nombre": "Nicolas Poussin", "anios": "1594–1665",
 "oficio": "Pintor francés",
 "patron": ["Nicolas Poussin"],
 "bio": "Nicolas Poussin nació en Les Andelys, Normandía, en 1594 y murió en Roma en 1665. Vivió en París desde 1612 y a comienzos de 1624, tras pasar por Venecia, llegó a Roma, donde transcurrió casi toda su vida. Tras la fría acogida de su Martirio de san Erasmo (1629) dejó de buscar encargos oficiales y pintó sobre todo cuadros de caballete para coleccionistas privados, como Cassiano dal Pozzo, que le encargó la primera serie de los Siete sacramentos. Su estancia en París de 1640 a 1642, al servicio de Luis XIII, lo dejó insatisfecho. Componía modelando figurillas de cera que disponía e iluminaba dentro de una caja.",
},
{
 "clave": "ribera", "nombre": "José de Ribera", "anios": "1591–1652",
 "oficio": "Pintor valenciano",
 "patron": ["José de Ribera"],
 "bio": "Hijo de un zapatero, nació en Játiva en 1591. Salió hacia Italia entre 1607 y 1609 y no volvió nunca: en 1611 trabajaba en Parma para los Farnesio, y en 1613 estaba en Roma, entre los seguidores de Caravaggio. En 1616 se instaló para siempre en Nápoles, capital del virreinato español, donde casó con la hija del pintor Giovan Bernardo Azzolino; fue conocido como «lo Spagnoletto». Sus primeras obras llevan el naturalismo caravaggesco a un realismo acentuado, a veces despiadado; desde 1630 aclara el color siguiendo a los venecianos. Murió en Nápoles el 3 de septiembre de 1652.",
},
{
 "clave": "bellini", "nombre": "Giovanni Bellini", "anios": "c. 1427–1516",
 "oficio": "Pintor veneciano",
 "patron": ["Giovanni Bellini"],
 "bio": "Giovanni Bellini nació en Venecia hacia 1427 según Vasari, fecha discutida; era hijo de Jacopo y probablemente hermano menor de Gentile. En 1453 su hermana Nicolosia se casó con Mantegna, cuya huella se ve en la «Oración en el huerto». Fue abandonando el temple al huevo por el óleo de origen flamenco, y quizá le influyó Antonello da Messina, en Venecia en 1475–1476. Desde hacia 1490 amplió un taller que formó a la generación siguiente. En 1506 Durero lo llamó «muy viejo y aún el mejor pintor de todos». Con más de ochenta y cinco años pintó el «Festín de los dioses» (1514). Murió en Venecia el 29 de noviembre de 1516.",
},
{
 "clave": "lemoyne", "nombre": "François Lemoyne", "anios": "1688–1737",
 "oficio": "Pintor francés",
 "patron": ["François Lemoyne"],
 "bio": "Nació en París en 1688 y murió allí el 4 de junio de 1737. Se formó con Louis Galloche y en la Academia real, que lo admitió en 1718. Entre 1723 y 1727 estuvo en Italia, donde estudió a Miguel Ángel, Correggio y Veronés. Su obra mayor es la Apoteosis de Hércules, techo del Salón de Hércules de Versalles con 142 figuras, cuyo boceto de 1732 conserva el Louvre. La terminó en 1736, tras cuatro años de trabajo, y Luis XV lo nombró primer pintor del rey; al año siguiente se suicidó, agotado por el encargo. Fueron alumnos suyos Natoire y, brevemente, Boucher.",
},
{
 "clave": "breu", "nombre": "Jörg Breu el Joven", "anios": "c. 1510–1547",
 "oficio": "Pintor y dibujante de Augsburgo",
 "patron": ["Jörg Breu el Joven"],
 "bio": "Hijo de Jörg Breu el Viejo, trabajó en el taller paterno como aprendiz y oficial y lo heredó en 1534. Fue pintor y dibujante para xilografía y vidriera. En 1536-1537 trabajó en Neuburg an der Donau para Otón Enrique del Palatinado, y de ese encargo quedan restos de frescos en el castillo de Grünau (1537). En 1538 pintó la sala de oficio de la casa de los tejedores de Augsburgo, y miniaturas para un manuscrito de lujo hoy en Eton College. Su monograma se parece al de su padre. Solo las obras que lo llevan permiten separarlos: sus figuras son más pequeñas y esbeltas, con paños más quebrados, de gusto ya manierista.",
},
{
 "clave": "villalpando", "nombre": "Cristóbal de Villalpando", "anios": "c. 1649–1714",
 "oficio": "Pintor novohispano",
 "patron": ["Cristóbal de Villalpando"],
 "bio": "Se desconoce la partida de bautismo de Cristóbal de Villalpando; en 1669 inició sus trámites matrimoniales en el Sagrario de la catedral de México, y de ahí se deduce que nació hacia 1649. Murió en la Ciudad de México el 20 de agosto de 1714. Su primera obra fechada es el retablo de Huaquechula, Puebla (1675). En la década de 1680 llegó a un estilo propio, de colores claros y pincelada suelta, que reinterpretaba a Rubens —conocido en Nueva España por grabados y copias— y a los madrileños Rizi y Carreño. El cabildo le encargó los cuatro lienzos monumentales de la sacristía de la catedral de México. En Puebla pintó la cúpula del Altar de los Reyes de la catedral.",
},
{
 "clave": "exekias", "nombre": "Exequias", "anios": "activo c. 550–525 a.C.",
 "oficio": "Ceramista y pintor de vasos ateniense",
 "patron": ["Exekias"],
 "bio": "Alfarero y pintor ateniense de figuras negras, activo hacia 550–525 a.C. o 540–520 a.C., se le considera, junto al Pintor de Amasis, el maestro más fino y original de la técnica a mediados del siglo VI a.C.. Empezó como alfarero del taller llamado Grupo E y luego decoró también sus vasos. Se conservan trece vasos con su firma: dos como alfarero y pintor, once solo como alfarero. Parece haber inventado formas nuevas, quizá la crátera de cáliz. En lugar de la acción, lo habitual entonces, pintaba el instante anterior o posterior —Aquiles y Áyax jugando en el ánfora del Vaticano—, dando peso a la psicología de la escena.",
},
{
 "clave": "eufronio", "nombre": "Eufronio", "anios": "activo c. 520–470 a.C.",
 "oficio": "Ceramista y pintor de vasos ateniense",
 "patron": ["Eufronio, ceramista y pintor ático"],
 "bio": "Eufronio trabajó en Atenas como pintor y alfarero de figuras rojas entre hacia 520 y 470 a.C.. La técnica, surgida hacia 520 a.C., invertía la de figuras negras: fondo barnizado de negro, figuras reservadas en el color de la arcilla y detalles pintados en línea fina en vez de incisos. Fue uno de los «Pioneros», que ensayaron escorzos y superposiciones del cuerpo; su crátera de Heracles y Anteo (Louvre G 103, hacia 515–510 a.C.) lo muestra. Firmó dieciocho vasos: seis como pintor y doce, posteriores, como alfarero, junto a Duris, Macrón y Onésimo; quizá le falló la vista, o quizá pasó a dirigir el taller.",
},
{
 "clave": "ingres", "nombre": "Jean-Auguste-Dominique Ingres", "anios": "1780–1867",
 "oficio": "Pintor francés",
 "patron": ["Jean-Auguste-Dominique Ingres"],
 "bio": "Nació en Montauban el 29 de agosto de 1780 y murió en París el 14 de enero de 1867. Su padre le enseñó dibujo y violín, y fue dos años segundo violín en la orquesta del Capitolio de Toulouse: de ahí la expresión francesa «violon d'Ingres». Entró en el taller de David en 1796 o 1797 y ganó el premio de Roma en 1801. Sostenía que «le dessin est la probité de l'art». La crítica le reprochó sus deformaciones anatómicas (a la Gran odalisca le sobraban, según uno, tres vértebras), que anticipan experimentos del siglo XX. Encabezó el clasicismo frente a Delacroix y dirigió la Academia de Francia en Roma entre 1834 y 1841.",
},
{
 "clave": "david", "nombre": "Jacques-Louis David", "anios": "1748–1825",
 "oficio": "Pintor francés",
 "patron": ["Jacques-Louis David"],
 "bio": "Discípulo de Joseph-Marie Vien, ganó el Premio de Roma en 1774 tras varios fracasos. El Juramento de los Horacios, expuesto en el Salón de 1785, se tomó como manifiesto de la vuelta a la Antigüedad. Jacobino cercano a Robespierre, en 1792 fue elegido diputado de la Convención y votó la ejecución de Luis XVI. Organizó fiestas nacionales y funerales de los mártires revolucionarios, y en 1793 pintó La muerte de Marat. Después fue pintor de Napoleón. Con la vuelta de los Borbones se exilió a Bruselas, donde murió. Entre sus alumnos figuraron Gérard, Gros e Ingres.",
},
{
 "clave": "matsch", "nombre": "Franz von Matsch", "anios": "1861–1942",
 "oficio": "Pintor y escultor austríaco",
 "patron": ["Franz von Matsch"],
 "bio": "Franz Matsch nació en Viena el 16 de septiembre de 1861 y murió allí en octubre de 1942. Desde 1875 estudió en la Kunstgewerbeschule, donde conoció a Gustav y Ernst Klimt; con ellos formó hacia 1879 la «Künstler-Compagnie», que decoró teatros de la monarquía y las escaleras del Burgtheater y del Kunsthistorisches Museum. Con Klimt recibió el encargo de las pinturas del Aula Magna de la Universidad de Viena; tras el escándalo de las de Klimt, que renunció en 1905, la colaboración terminó y Matsch volvió al historicismo. Retratista solicitado por la casa imperial, fue ennoblecido en 1912 y diseñó el reloj Anker de Viena.",
},
{
 "clave": "hamilton", "nombre": "Gavin Hamilton", "anios": "1723–1798",
 "oficio": "Pintor y anticuario escocés",
 "patron": ["Gavin Hamilton"],
 "bio": "Nacido en 1723 en Lanarkshire y educado en la Universidad de Glasgow, estudió en Roma con Agostino Masucci, pintó retratos de la aristocracia en Londres a comienzos de la década de 1750 y en 1756 volvió a Roma para quedarse. Allí fue pintor, arqueólogo y marchante: excavó yacimientos antiguos de los alrededores y vendió muchos hallazgos a coleccionistas británicos. Entre 1760 y 1775 pintó seis grandes escenas de la Ilíada, cada una para un mecenas distinto; los grabados de Domenico Cunego les dieron audiencia internacional, y sus lienzos influyeron en la generación francesa siguiente, sobre todo en Jacques-Louis David. Murió en Roma el 4 de enero de 1798.",
},
{
 "clave": "ivanov", "nombre": "Aleksandr Ivánov", "anios": "1806–1858",
 "oficio": "Pintor ruso",
 "patron": ["Alexander Andreyevich Ivanov"],
 "bio": "Aleksandr Ivánov nació en San Petersburgo en 1806. Llegó a Roma en octubre de 1830 y vivió veintiocho años en Italia. De 1837 a 1857 pintó «La aparición de Cristo al pueblo», hoy en la Galería Tretiakov; se conservan más de trescientos estudios en la Tretiakov y setenta y siete en el Museo Ruso. Al final, a partir de la «Vida de Jesús» de Strauss, proyectó una serie bíblica. En 1858 volvió a San Petersburgo; el cuadro, expuesto en el Palacio de Invierno y en la Academia, fue recibido con indiferencia. Murió de cólera en casa de los hermanos Botkin, horas antes de que el emperador quisiera comprarlo por 15.000 rublos.",
},
{
 "clave": "tiepolo_g", "nombre": "Giambattista Tiepolo", "anios": "1696–1770",
 "oficio": "Pintor veneciano",
 "patron": ["Giambattista Tiepolo"],
 "bio": "Nació en Venecia, probablemente el 5 de marzo de 1696. Discípulo de Gregorio Lazzarini, maduró como fresquista en Udine y en los palacios Archinto y Dugnani de Milán. En diciembre de 1750 llegó a Wurzburgo con sus hijos Domenico y Lorenzo, y allí pintó el Kaisersaal y la escalera de la Residenz, firmada en 1753. Carlos III lo llamó para decorar el Palacio Real, y llegó a Madrid el 4 de junio de 1762. En una corte donde pesaba Mengs, el medio oficial le fue hostil. Murió de repente en Madrid la noche del 26 al 27 de marzo de 1770.",
},
{
 "clave": "tiepolo_d", "nombre": "Giandomenico Tiepolo", "anios": "1727–1804",
 "oficio": "Pintor veneciano",
 "patron": ["Giovanni Domenico Tiepolo"],
 "bio": "Hijo de Giambattista y de Cecilia Guardi, se formó en el taller paterno. Debutó en Venecia en 1747 con un vía crucis para el oratorio de San Polo. Entre 1750 y 1753 estuvo en Wurzburgo con su padre y su hermano Lorenzo: pintó las sobrepuertas del Kaisersaal y grabó las Idee pittoresche sopra la Fuga in Egitto. En 1762 los acompañó a Madrid, y en el Palacio Real pintó por su cuenta la Glorificación de España. En 1770, muerto el padre, volvió a Venecia. En la villa familiar de Zianigo fechó en 1797 los frescos de la sala de los Pulcinella, año del álbum de dibujos Divertimento per li regazzi.",
},
{
 "clave": "van_dyck", "nombre": "Antoon van Dyck", "anios": "1599–1641",
 "oficio": "Pintor flamenco",
 "patron": ["Anton van Dyck"],
 "bio": "Antoon van Dyck nació en Amberes en 1599 y murió en Londres en 1641. A los diez años entró en el taller de Hendrick van Balen y hacia los diecisiete ya trabajaba por su cuenta. Hacia 1618, año en que ingresó como maestro en la guilda de San Lucas, colaboró brevemente con Rubens. Tras una corta estancia en Londres (1621) pasó a Italia hasta 1627 y fue el retratista de la aristocracia genovesa. En 1632 se instaló en Londres como pintor de corte de Carlos I. Sus retratos del rey y su familia fijaron una nueva norma para el retrato inglés y ejercieron un influjo determinante sobre la retratística británica del siglo XVIII.",
},
{
 "clave": "vernet", "nombre": "Carle Vernet", "anios": "1758–1836",
 "oficio": "Pintor y litógrafo francés",
 "patron": ["Carle Vernet"],
 "bio": "Antoine-Charles-Horace Vernet, llamado Carle, nació en Burdeos en 1758 y se formó con su padre, Claude-Joseph Vernet. En 1782 ganó el Prix de Rome. Su hermana Émilie, pintora, fue detenida el 25 de junio de 1794 y guillotinada el 24 de julio. En 1808 Napoleón le concedió la Legión de Honor por una de sus escenas de batalla. Se le conoció sobre todo como pintor de caballos en movimiento: carreras, cacerías, caballería; desde 1816 se dedicó a estampas de vendedores callejeros, mercados de caballos y dandis, muchas de ellas litografías. Fomentó el talento de su hijo Horace. Murió en París en 1836.",
},
{
 "clave": "laocoonte", "nombre": "Agesandro, Polidoro y Atenodoro", "anios": "activos c. siglo I a.C.",
 "oficio": "Escultores rodios",
 "patron": ["Agesandro, Polidoro y Atenodoro de Rodas"],
 "bio": "Plinio el Viejo alaba el Laocoonte del palacio de Tito como obra superior a toda pintura o escultura, hecha de común acuerdo por Agesandro, Polidoro y Atenodoro, de Rodas, y afirma que salió de un solo bloque. Ya en 1898 el diccionario de Harper juzgaba inexacta esa afirmación. El grupo apareció en 1506 en el Esquilino, se identificó enseguida con el de Plinio y lo compró Julio II; los Museos Vaticanos lo fechan hacia 40–30 a.C., con debate. La Getty ULAN los hace emigrar a Italia a comienzos del Imperio y les atribuye algunos o todos los grupos de la gruta de Tiberio en Sperlonga, hallados en 1957.",
},
{
 "clave": "behzad", "nombre": "Kamāl ud-Dīn Behzad", "anios": "m. c. 1535",
 "oficio": "Pintor persa de la corte timúrida y safávida",
 "patron": ["Kamāl ud-Dīn Behzad"],
 "bio": "Kamal al-Din Behzad trabajó en Herat bajo el timúrida Husayn Bayqara (1470-1506), primero para Mir Ali Shir Navai y luego para el sultán, a las órdenes de Mirak Naqqash, que lo crió tras quedar huérfano. Después de 1506 su vida está mal documentada; Babur lo vincula con Shaybani Khan, señor de Herat en 1507-1510. Pasó sus últimos años en Tabriz al servicio del sha Tahmasp; el decreto de 1522 que lo pone al frente del taller real es de autenticidad dudosa. Murió hacia 1535-1536 y fue enterrado en Tabriz. Sus obras seguras son las pinturas firmadas del Bustán de Saadí de El Cairo (1488-1489). Su estilo influyó en Bujará y en la India mogol.",
},
{
 "clave": "bouguereau", "nombre": "William Bouguereau", "anios": "1825–1905",
 "oficio": "Pintor académico francés",
 "patron": ["William Bouguereau"],
 "bio": "Nacido en La Rochelle, estudió en la École des Beaux-Arts y ganó el Premio de Roma en 1850. A su regreso decoró varias mansiones inspirándose en los frescos de Pompeya y Herculano. Recibió una medalla de honor en la Exposición de París de 1878 y otra en el Salón de 1885. Con Alexandre Cabanel fue el defensor más influyente del academicismo francés: dibujo preciso, contorno y acabado. Contra eso se rebelaron los impresionistas. Sus escenas campesinas se las disputaban los coleccionistas estadounidenses. En 1984 una gran retrospectiva recorrió el Petit Palais de París, el Museo de Bellas Artes de Montreal y el Wadsworth Atheneum de Hartford.",
},
{
 "clave": "marianos", "nombre": "Marianos y su hijo Hanina", "anios": "activos s. VI",
 "oficio": "Mosaiquistas judíos de Galilea",
 "patron": ["Marianos y su hijo Hanina, sinagoga de Beit Alfa"],
 "bio": "Marianos y su hijo Hanina solo se conocen por dos pavimentos de mosaico. En la sinagoga de Beit Alfa, descubierta en 1929 por miembros del kibutz y excavada ese año por E. L. Sukenik, una inscripción griega pide que se recuerde a «los artesanos que realizaron esta obra, Marianos y su hijo Hanina». Otra, en arameo, fecha el suelo en el reinado del emperador Justino, probablemente Justino I (518–527). Sus nombres reaparecen en un mosaico de una sinagoga de Beit Shean excavada por Nehemya Zori en 1962, que conserva inscripciones griegas y en alfabeto samaritano. Trabajaban en la manera grecooriental de la época: frontalidad, motivos repetidos, sin modelado ni perspectiva.",
},
]
