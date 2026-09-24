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
 "bio": "Se consideraba escultor antes que pintor y aceptó el encargo de la Capilla Sixtina a regañadientes: Julio II lo apartó del proyecto que de verdad le importaba, su propia tumba, para mandarlo a pintar un techo. Trabajó en él de 1508 a 1512, de pie y con la cabeza hacia atrás —no tumbado, como cuenta la leyenda—, y salió con la vista dañada durante meses. En sus 343 figuras el cuerpo humano hace todo el trabajo: no hay paisaje, ni arquitectura pintada, ni atributos; solo anatomía y gesto.",
},
{
 "clave": "masaccio", "nombre": "Masaccio", "anios": "1401–1428",
 "oficio": "Pintor florentino",
 "patron": ["Masaccio"],
 "bio": "Murió a los veintisiete años y cambió la pintura europea en menos de una década. Fue el primero en aplicar a la figura pintada la perspectiva que Brunelleschi había demostrado en arquitectura y en hacer que la luz de un fresco viniera de donde de verdad entra la luz en la capilla. Vasari cuenta que durante un siglo los pintores florentinos —Miguel Ángel entre ellos— fueron a la Brancacci a copiarlo.",
},
{
 "clave": "tiziano", "nombre": "Tiziano Vecellio", "anios": "c. 1488–1576",
 "oficio": "Pintor veneciano",
 "patron": ["Tiziano Vecellio"],
 "bio": "Pintor de Carlos V y de Felipe II, fue el primer artista europeo que trabajó para media Europa sin moverse de Venecia. Su última manera, de pincelada suelta y forma deshecha, desconcertó a sus contemporáneos: Vasari escribió que de cerca sus cuadros tardíos no se entendían y solo funcionaban a distancia. Murió durante la peste de 1576, muy anciano, sin que se sepa su edad exacta.",
},
{
 "clave": "bruegel", "nombre": "Pieter Bruegel el Viejo", "anios": "c. 1525–1569",
 "oficio": "Pintor y grabador flamenco",
 "patron": ["Pieter Bruegel el Viejo"],
 "bio": "Viajó a Italia cruzando los Alpes y volvió sin apenas rastro italiano en su pintura, salvo el paisaje de montaña, que no olvidó nunca. Se le llamó «el campesino» por sus escenas de aldea, pero trabajaba para coleccionistas cultos de Amberes y Bruselas. Sus dos hijos siguieron pintando y copiando sus composiciones durante décadas, lo que ha complicado para siempre distinguir originales de repeticiones.",
},
{
 "clave": "cormon", "nombre": "Fernand Cormon", "anios": "1845–1924",
 "oficio": "Pintor francés",
 "patron": ["Fernand Cormon"],
 "bio": "Pintor de historia y prehistoria de gran formato, hoy se le recuerda sobre todo por su taller: por él pasaron Van Gogh, Toulouse-Lautrec y Émile Bernard. Enseñaba de manera académica a alumnos que iban a romper con lo académico, y los dejó hacer.",
},
{
 "clave": "blake", "nombre": "William Blake", "anios": "1757–1827",
 "oficio": "Poeta, grabador y pintor inglés",
 "patron": ["William Blake"],
 "bio": "Inventó una técnica propia —el grabado en relieve iluminado— para no depender de impresores ni editores: escribía e ilustraba directamente sobre la plancha y coloreaba a mano cada ejemplar, de modo que no hay dos copias iguales de ninguno de sus libros. Vendió poquísimo en vida y murió en la pobreza. Su mitología personal, con Urizen como dios de la razón y la medida, invierte la teología cristiana: para Blake, crear el mundo midiéndolo es el primer acto de tiranía.",
},
{
 "clave": "turner", "nombre": "J. M. W. Turner", "anios": "1775–1851",
 "oficio": "Pintor y acuarelista inglés",
 "patron": ["J.M.W. Turner"],
 "bio": "Entró en la Royal Academy con catorce años y acabó dejando al Estado británico casi trescientos lienzos y treinta mil obras sobre papel. Su pintura tardía disuelve el motivo en luz y atmósfera hasta un punto que sus contemporáneos leyeron como obra sin acabar. Vivió sus últimos años bajo nombre falso en Chelsea, donde los vecinos lo conocían como «el almirante Booth».",
},
{
 "clave": "dore", "nombre": "Gustave Doré", "anios": "1832–1883",
 "oficio": "Ilustrador, grabador y pintor francés",
 "patron": ["Gustave Doré"],
 "bio": "El ilustrador más difundido del siglo XIX: la Biblia, Dante, Cervantes, Milton y Perrault pasaron por su mano y por un taller de más de cuarenta grabadores que trasladaban sus dibujos a la madera. Su imaginería fijó durante generaciones el aspecto que «debían» tener el infierno de Dante y el Diluvio. Ambicionaba ser reconocido como pintor y nunca lo consiguió del todo.",
},
{
 "clave": "scorel", "nombre": "Jan van Scorel", "anios": "1495–1562",
 "oficio": "Pintor neerlandés",
 "patron": ["Jan van Scorel"],
 "bio": "Viajó a Jerusalén y luego a Roma, donde el papa Adriano VI —neerlandés como él— lo puso al frente de las colecciones de arte del Vaticano. Volvió al norte convertido en el gran introductor del Renacimiento italiano en los Países Bajos, y fue además canónigo, ingeniero de drenajes y organista.",
},
{
 "clave": "watts", "nombre": "George Frederic Watts", "anios": "1817–1904",
 "oficio": "Pintor y escultor inglés",
 "patron": ["George Frederic Watts"],
 "bio": "Pintor de alegorías morales en una Inglaterra que prefería la anécdota, rechazó dos veces el título de barón y regaló buena parte de su obra a la nación. Quiso pintar «ideas, no cosas». Su galería en Compton, levantada por él mismo, sigue siendo el mejor sitio para verlo.",
},
{
 "clave": "danby", "nombre": "Francis Danby", "anios": "1793–1861",
 "oficio": "Pintor irlandés",
 "patron": ["Francis Danby"],
 "bio": "Formó en Bristol un grupo de paisajistas y luego compitió en Londres con John Martin en el género del desastre bíblico a gran escala. Un escándalo doméstico lo obligó a marcharse al continente durante once años, tiempo que pasó en Suiza construyendo barcas de vela, y su carrera nunca se recuperó del todo.",
},
{
 "clave": "cole", "nombre": "Thomas Cole", "anios": "1801–1848",
 "oficio": "Pintor angloamericano",
 "patron": ["Thomas Cole"],
 "bio": "Nacido en Lancashire y emigrado a los diecisiete años, fundó la Escuela del Río Hudson, la primera corriente pictórica propiamente estadounidense. Alternó el paisaje observado con ciclos alegóricos sobre el auge y la caída de los imperios, en los que la naturaleza siempre sobrevive a la civilización que la ocupó.",
},
{
 "clave": "cranach", "nombre": "Lucas Cranach el Viejo", "anios": "1472–1553",
 "oficio": "Pintor y grabador alemán",
 "patron": ["Lucas Cranach el Viejo"],
 "bio": "Pintor de corte en Wittenberg, amigo de Lutero y padrino de uno de sus hijos, fue también impresor, boticario y alcalde de la ciudad. Su taller funcionaba casi como una industria: repitió el tema de Adán y Eva decenas de veces con variaciones mínimas, y esa producción en serie es la razón de que el mismo cuadro exista en tantos museos.",
},
{
 "clave": "durero", "nombre": "Alberto Durero", "anios": "1471–1528",
 "oficio": "Pintor, grabador y teórico alemán",
 "patron": ["Alberto Durero"],
 "bio": "Hijo de orfebre, llevó el grabado a una precisión que nadie había alcanzado y fue el primer artista del norte en pensarse a sí mismo como intelectual: escribió tratados sobre proporción humana, perspectiva y fortificación. Firmaba con un monograma que se falsificó tanto en vida que llegó a pleitear por él en Venecia.",
},
{
 "clave": "caravaggio", "nombre": "Caravaggio", "anios": "1571–1610",
 "oficio": "Pintor lombardo",
 "patron": ["Caravaggio"],
 "bio": "Pintaba del natural, sin dibujo previo, con modelos de la calle y una luz de foco que sacaba las figuras de la oscuridad. Mató a un hombre en una reyerta en 1606 y pasó sus últimos cuatro años huyendo por Nápoles, Malta y Sicilia con una condena de muerte encima. Murió a los treinta y ocho en circunstancias que aún se discuten.",
},
{
 "clave": "rembrandt", "nombre": "Rembrandt van Rijn", "anios": "1606–1669",
 "oficio": "Pintor y grabador neerlandés",
 "patron": ["Rembrandt van Rijn", "Rembrandt van Rijn y taller"],
 "bio": "Se pintó a sí mismo unas ochenta veces a lo largo de cuarenta años, de joven acomodado a anciano arruinado, en la serie de autorretratos más extensa del arte europeo. Llegó a la cima del mercado de Ámsterdam y quebró en 1656; el inventario de su bancarrota, que se conserva, es una de las mejores descripciones que existen del taller de un pintor del siglo XVII.",
},
{
 "clave": "rubliov", "nombre": "Andréi Rubliov", "anios": "c. 1360–1428",
 "oficio": "Monje e iconógrafo ruso",
 "patron": ["Andréi Rubliov"],
 "bio": "Monje del monasterio de Andrónikov, es el único pintor de iconos al que la Iglesia ortodoxa rusa ha canonizado, en 1988. De su vida apenas se sabe nada seguro y la atribución de casi toda su obra se discute; solo la Trinidad está documentada como suya sin dudas serias.",
},
{
 "clave": "delacroix", "nombre": "Eugène Delacroix", "anios": "1798–1863",
 "oficio": "Pintor francés",
 "patron": ["Eugène Delacroix"],
 "bio": "Cabeza del romanticismo francés frente al clasicismo de Ingres, con quien mantuvo una rivalidad que dividió a la crítica de su tiempo. Un viaje a Marruecos en 1832 le dio un repertorio de luz y color que explotó el resto de su vida. Su diario, publicado póstumamente, es uno de los grandes textos de un pintor sobre su oficio.",
},
{
 "clave": "gauguin", "nombre": "Paul Gauguin", "anios": "1848–1903",
 "oficio": "Pintor francés",
 "patron": ["Paul Gauguin"],
 "bio": "Fue agente de bolsa hasta los treinta y cinco años y lo dejó todo por pintar. Buscó en Bretaña primero y en Polinesia después una vida que creía anterior a la civilización europea, y construyó allí una obra de color plano y contorno marcado que abrió camino al simbolismo y al fauvismo. Murió en las Marquesas, endeudado y enfermo.",
},
{
 "clave": "corot", "nombre": "Camille Corot", "anios": "1796–1875",
 "oficio": "Pintor francés",
 "patron": ["Jean-Baptiste-Camille Corot"],
 "bio": "Puente entre el paisaje neoclásico y el impresionismo, pintaba del natural pequeños estudios que hoy se aprecian más que sus grandes composiciones de salón. Tuvo fama de generoso hasta lo temerario: mantuvo a la viuda de Millet y a Daumier ciego, y firmó cuadros de amigos necesitados para que pudieran venderlos, lo que ha convertido su catálogo en un problema de atribución permanente.",
},
{
 "clave": "velazquez", "nombre": "Diego Velázquez", "anios": "1599–1660",
 "oficio": "Pintor sevillano",
 "patron": ["Diego Velázquez"],
 "bio": "Pintor de cámara de Felipe IV desde los veinticuatro años, pasó la vida en la corte ocupado además en cargos palaciegos que le robaban tiempo de taller. Dos viajes a Italia le cambiaron la manera. Su obra es escasa —poco más de un centenar de cuadros— y de una economía de medios que solo se aprecia de cerca: manchas sueltas que a distancia se vuelven encaje y plata.",
},
{
 "clave": "john_martin", "nombre": "John Martin", "anios": "1789–1854",
 "oficio": "Pintor y grabador inglés",
 "patron": ["John Martin"],
 "bio": "Especialista en la catástrofe bíblica de formato descomunal, con multitudes diminutas aplastadas por arquitecturas y cataclismos. Tuvo un éxito popular enorme gracias a las estampas, y un desprecio crítico casi igual de grande. Dedicó años a proyectos de ingeniería para el alcantarillado de Londres que nadie le compró.",
},
{
 "clave": "bosco", "nombre": "El Bosco", "anios": "c. 1450–1516",
 "oficio": "Pintor brabanzón",
 "patron": ["Hieronymus Bosch, El Bosco"],
 "bio": "Vivió toda su vida en la misma ciudad, Bolduque, de la que tomó el nombre con que firmaba. No se conserva ni un solo escrito suyo, de modo que todo lo que se dice sobre el significado de sus criaturas es interpretación. Felipe II reunió sus tablas y por eso el Prado tiene hoy la mejor colección del mundo de un pintor que nunca pisó España.",
},
{
 "clave": "rubens", "nombre": "Peter Paul Rubens", "anios": "1577–1640",
 "oficio": "Pintor flamenco",
 "patron": ["Peter Paul Rubens"],
 "bio": "Además de pintor fue diplomático al servicio de los Habsburgo y negoció la paz entre España e Inglaterra, que le valió el título de caballero de las dos coronas. Hablaba seis lenguas y dirigía en Amberes el taller más productivo de Europa, con Van Dyck entre sus colaboradores. Sus bocetos de su propia mano suelen preferirse hoy a los grandes lienzos acabados por el taller.",
},
{
 "clave": "poussin", "nombre": "Nicolas Poussin", "anios": "1594–1665",
 "oficio": "Pintor francés",
 "patron": ["Nicolas Poussin"],
 "bio": "Francés de nacimiento y romano de vida: pasó en Roma casi cuarenta años y volvió a París solo dos, mal avenido con la corte. Trabajaba para un círculo pequeño de coleccionistas eruditos, componía con figuritas de cera dispuestas en cajas y defendía que la pintura se dirige a la inteligencia. Su nombre acabó designando toda una manera de entender el clasicismo.",
},
{
 "clave": "ribera", "nombre": "José de Ribera", "anios": "1591–1652",
 "oficio": "Pintor valenciano",
 "patron": ["José de Ribera"],
 "bio": "Nació en Játiva y se instaló muy joven en Nápoles, entonces española, donde vivió el resto de su vida y donde se le llamó «lo Spagnoletto». Llevó el naturalismo de Caravaggio a un extremo táctil: pieles gastadas, pies sucios, arrugas, en santos y filósofos tratados como campesinos.",
},
{
 "clave": "bellini", "nombre": "Giovanni Bellini", "anios": "c. 1430–1516",
 "oficio": "Pintor veneciano",
 "patron": ["Giovanni Bellini"],
 "bio": "Fundó la escuela veneciana del color junto a su hermano Gentile y su cuñado Mantegna, y tuvo por alumnos a Giorgione y a Tiziano. Adoptó el óleo cuando en Venecia todavía se pintaba al temple y con él consiguió una luz húmeda que se convirtió en la marca de la ciudad. Siguió cambiando de estilo hasta pasados los ochenta años.",
},
{
 "clave": "lemoyne", "nombre": "François Lemoyne", "anios": "1688–1737",
 "oficio": "Pintor francés",
 "patron": ["François Lemoyne"],
 "bio": "Primer pintor del rey y autor del techo del Salón de Hércules de Versalles, que le costó cuatro años. Al día siguiente de recibir un encargo mayor se quitó la vida con su espada, agotado por el trabajo y por la muerte de su mujer. Fue maestro de Boucher y uno de los que llevaron la pintura francesa del gran estilo al rococó.",
},
{
 "clave": "breu", "nombre": "Jörg Breu el Joven", "anios": "c. 1510–1547",
 "oficio": "Pintor y dibujante de Augsburgo",
 "patron": ["Jörg Breu el Joven"],
 "bio": "Hijo y continuador del taller de su padre en Augsburgo, trabajó sobre todo en diseños para vidriera y en pequeñas tablas de tema bíblico. Murió joven y su obra se ha confundido a menudo con la paterna, un problema habitual en los talleres familiares alemanes del XVI.",
},
{
 "clave": "villalpando", "nombre": "Cristóbal de Villalpando", "anios": "c. 1649–1714",
 "oficio": "Pintor novohispano",
 "patron": ["Cristóbal de Villalpando"],
 "bio": "El pintor más ambicioso del barroco novohispano, activo en la Ciudad de México y en Puebla. Trabajaba a una escala enorme —la cúpula del Ochavo de la catedral poblana, la sacristía de la catedral metropolitana— con una pincelada suelta y un color encendido que no dependen ya de los modelos europeos que le llegaban grabados.",
},
{
 "clave": "exekias", "nombre": "Exequias", "anios": "activo c. 550–525 a.C.",
 "oficio": "Ceramista y pintor de vasos ateniense",
 "patron": ["Exekias"],
 "bio": "El mayor pintor de figuras negras del Ática, y uno de los pocos que firmaba a la vez como alfarero y como pintor, señal de que hacía el vaso entero. Prefería el instante anterior o posterior a la acción —Aquiles y Áyax jugando a los dados mientras fuera hay guerra— en vez de la acción misma, y esa elección es lo que lo separa de todos sus contemporáneos.",
},
{
 "clave": "eufronio", "nombre": "Eufronio", "anios": "activo c. 520–470 a.C.",
 "oficio": "Ceramista y pintor de vasos ateniense",
 "patron": ["Eufronio, ceramista y pintor ático"],
 "bio": "De la primera generación que pintó de figuras rojas, invirtiendo la técnica: en vez de siluetas negras sobre arcilla, arcilla clara reservada sobre fondo negro, lo que permitía dibujar la anatomía con pincel en lugar de rascarla. Firmó como pintor de joven y como alfarero de mayor, quizá porque la vista dejó de acompañarle.",
},
{
 "clave": "ingres", "nombre": "Jean-Auguste-Dominique Ingres", "anios": "1780–1867",
 "oficio": "Pintor francés",
 "patron": ["Jean-Auguste-Dominique Ingres"],
 "bio": "Alumno de David y guardián del clasicismo frente al romanticismo de Delacroix, defendía que el dibujo es la probidad del arte. Deformaba sin embargo la anatomía sin escrúpulo cuando la línea lo pedía —cuellos y espaldas imposibles—, algo que sus críticos le echaron en cara y que sus herederos del siglo XX celebraron. Tocaba el violín lo bastante bien como para dejar una expresión al idioma francés.",
},
{
 "clave": "david", "nombre": "Jacques-Louis David", "anios": "1748–1825",
 "oficio": "Pintor francés",
 "patron": ["Jacques-Louis David"],
 "bio": "Pintor de la Revolución y luego de Napoleón, fue diputado, votó la muerte del rey y organizó las fiestas cívicas del nuevo régimen. Con la Restauración se exilió a Bruselas, donde murió sin volver a Francia. Su neoclasicismo de contornos duros y gesto contenido fue durante treinta años el estilo oficial de un país en revolución permanente.",
},
{
 "clave": "matsch", "nombre": "Franz von Matsch", "anios": "1861–1942",
 "oficio": "Pintor y escultor austríaco",
 "patron": ["Franz von Matsch"],
 "bio": "Formó con Gustav Klimt y su hermano Ernst la «Compañía de Artistas» que decoró teatros y museos por todo el imperio austrohúngaro. Cuando Klimt rompió hacia la Secesión, Matsch se quedó en el academicismo y prosperó como retratista de la corte, lo que explica que hoy se le recuerde mucho menos.",
},
{
 "clave": "hamilton", "nombre": "Gavin Hamilton", "anios": "1723–1798",
 "oficio": "Pintor y anticuario escocés",
 "patron": ["Gavin Hamilton"],
 "bio": "Pintor, arqueólogo y marchante en Roma, excavó en Hadriano y en Ostia y vendió a la aristocracia británica buena parte de las antigüedades que hoy están en Inglaterra. Sus escenas homéricas, difundidas por grabado, fueron una de las fuentes del neoclasicismo europeo, David incluido.",
},
{
 "clave": "ivanov", "nombre": "Aleksandr Ivánov", "anios": "1806–1858",
 "oficio": "Pintor ruso",
 "patron": ["Alexander Andreyevich Ivanov"],
 "bio": "Pasó veinte años en Roma pintando un solo cuadro, «La aparición de Cristo al pueblo», para el que hizo más de seiscientos estudios. Volvió a San Petersburgo con él en 1858 y murió de cólera semanas después de exponerlo, con una acogida tibia.",
},
{
 "clave": "tiepolo_g", "nombre": "Giambattista Tiepolo", "anios": "1696–1770",
 "oficio": "Pintor veneciano",
 "patron": ["Giambattista Tiepolo"],
 "bio": "El último gran fresquista italiano, capaz de resolver bóvedas enteras con cielos altísimos y figuras vistas en escorzo desde abajo. Trabajó en Venecia, en Wurzburgo y finalmente en Madrid, donde murió al servicio de Carlos III mientras el gusto giraba ya hacia el neoclasicismo que su obra hacía parecer antigua.",
},
{
 "clave": "tiepolo_d", "nombre": "Giandomenico Tiepolo", "anios": "1727–1804",
 "oficio": "Pintor veneciano",
 "patron": ["Giovanni Domenico Tiepolo"],
 "bio": "Hijo y principal colaborador de Giambattista, lo acompañó a Wurzburgo y a Madrid. Cuando quedó libre de la sombra paterna desarrolló una obra propia, más irónica y terrena, poblada de payasos y escenas de la Venecia que se acababa.",
},
{
 "clave": "van_dyck", "nombre": "Antoon van Dyck", "anios": "1599–1641",
 "oficio": "Pintor flamenco",
 "patron": ["Anton van Dyck"],
 "bio": "Niño prodigio de Amberes y principal colaborador de Rubens antes de los veinte años, acabó en Londres como pintor de cámara de Carlos I. Su manera de retratar —figura alargada, pose desenvuelta, mirada de lado— fijó el modelo del retrato aristocrático inglés durante siglo y medio.",
},
{
 "clave": "vernet", "nombre": "Carle Vernet", "anios": "1758–1836",
 "oficio": "Pintor y litógrafo francés",
 "patron": ["Carle Vernet"],
 "bio": "Segundo de una dinastía de tres pintores —hijo de Joseph, padre de Horace—, se especializó en el caballo y en la batalla. La ejecución de su hermana durante el Terror lo apartó de la pintura durante años; volvió con Napoleón, para quien pintó campañas, y terminó como uno de los primeros litógrafos franceses.",
},
{
 "clave": "laocoonte", "nombre": "Agesandro, Polidoro y Atenodoro", "anios": "activos c. siglo I a.C.",
 "oficio": "Escultores rodios",
 "patron": ["Agesandro, Polidoro y Atenodoro de Rodas"],
 "bio": "Plinio el Viejo los nombra como autores del Laocoonte y dice que trabajaron los tres en una sola pieza de mármol, algo que la restauración moderna ha desmentido: son varios bloques. No se conserva ninguna otra obra firmada por ellos, ni retrato, ni más datos que esa línea de Plinio y las firmas halladas en Sperlonga.",
},
{
 "clave": "behzad", "nombre": "Kamāl ud-Dīn Behzad", "anios": "c. 1450–1535",
 "oficio": "Pintor persa de la corte timúrida y safávida",
 "patron": ["Kamāl ud-Dīn Behzad"],
 "bio": "Se formó y trabajó en Herat, en el actual Afganistán, al servicio del sultán timúrida Husayn Bayqara, y cuando la ciudad pasó a los safávidas se trasladó a Tabriz, donde el sha Ismail lo puso en 1522 al frente de la biblioteca real. Sus figuras, con gestos de la vida cotidiana y rostros individualizados, y sus arquitecturas escalonadas marcaron la pintura persa, otomana y mogol durante un siglo; tantas obras se le atribuyeron después que las pocas páginas firmadas, como las del Bustán de El Cairo, son la referencia para distinguir lo suyo.",
},
{
 "clave": "bouguereau", "nombre": "William Bouguereau", "anios": "1825–1905",
 "oficio": "Pintor académico francés",
 "patron": ["William Bouguereau"],
 "bio": "Nacido en La Rochelle, ganó el Premio de Roma en 1850 y fue durante medio siglo el pintor más prestigioso de la Academia y del Salón de París, con un acabado tan pulido que no se ve la pincelada. Los impresionistas hicieron de él el emblema de todo lo que combatían, y el siglo XX lo olvidó hasta la exposición retrospectiva de 1984. Muchos de sus grandes lienzos cruzaron el Atlántico en vida, comprados por coleccionistas de Estados Unidos y de Argentina.",
},
{
 "clave": "marianos", "nombre": "Marianos y su hijo Hanina", "anios": "activos s. VI",
 "oficio": "Mosaiquistas judíos de Galilea",
 "patron": ["Marianos y su hijo Hanina, sinagoga de Beit Alfa"],
 "bio": "Todo lo que se sabe de ellos son dos firmas en griego: la del pavimento de la sinagoga de Beit Alfa y la de una sinagoga samaritana de la cercana Beit Shean. Eran padre e hijo —el nombre del padre, griego; el del hijo, hebreo— y trabajaban con un estilo popular de figuras planas y ojos enormes, sin la pretensión clásica de los talleres de Antioquía. No se conserva ningún retrato suyo.",
},
]
