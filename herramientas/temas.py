# -*- coding: utf-8 -*-
"""Temas que cruzan los libros: el mismo pasaje contado en textos distintos.

Cada tema dice qué pasajes lo cuentan —con referencia exacta: libro, capítulo, tablilla,
canto y verso, comprobable en cualquier edición— y qué obras de la colección lo representan.
La introducción solo afirma lo que dicen esos pasajes; las lecturas y atribuciones de cada
obra están en su propia página, con sus fuentes.

Las obras se nombran por libro y por el NÚMERO de su archivo (el «42» de 42_Las_Capillas…),
que no cambia aunque cambie el orden de la colección. paginas.py comprueba al construir que
cada una existe.

Para añadir un tema: una entrada más en TEMAS. La página, el índice y los enlaces desde cada
obra se generan solos.
"""

TEMAS = [
{
 "clave": "diluvio",
 "titulo": "El Diluvio",
 "lema": "Un dios decide acabar con la humanidad y uno solo se salva en una nave: la misma historia en tres libros.",
 "intro": "En el Atrahasis, Enlil manda el Diluvio porque el ruido de los hombres no le deja dormir, y Ea avisa a Atrahasis hablándole a la pared de cañas de su casa. En Gilgamesh, Utnapishtim cuenta a Gilgamesh el mismo relato, con la nave calafateada con betún, la tormenta de seis días y siete noches y las aves que suelta al final: una paloma, una golondrina y un cuervo, que no vuelve. En el Génesis, Noé suelta un cuervo y después una paloma tres veces. En los tres, el superviviente ofrece un sacrificio al salir de la nave.",
 "pasajes": [
  ("atrahasis", "Atrahasis, tablilla III", "El aviso a través de la pared de cañas, la nave, la tormenta de siete días y siete noches, y el sacrificio al que acuden los dioses hambrientos."),
  ("gilgamesh", "Gilgamesh, tablilla XI, 1–206", "Utnapishtim narra el Diluvio: la nave, la tormenta, el monte Nimush y las tres aves."),
  ("genesis", "Génesis 6,5 – 9,17", "El arca, los cuarenta días, el cuervo y la paloma, el sacrificio de Noé y el arco iris."),
  ("genesis", "Génesis 9,18–27", "Después del Diluvio: la embriaguez de Noé."),
 ],
 "obras": [("atrahasis", "01"), ("atrahasis", "03"), ("atrahasis", "04"), ("gilgamesh", "01"),
           ("genesis", "04"), ("genesis", "10"), ("genesis", "40"), ("genesis", "31"),
           ("genesis", "08"), ("genesis", "42"), ("genesis", "44"), ("genesis", "47"),
           ("genesis", "11"), ("genesis", "12"), ("genesis", "13"), ("genesis", "32")],
},
{
 "clave": "barro",
 "titulo": "El ser humano hecho de barro",
 "lema": "Arcilla y el aliento o la sangre de un dios: cuatro textos cuentan así el origen del hombre.",
 "intro": "En el Génesis, Dios forma al hombre con el polvo del suelo y le insufla en la nariz aliento de vida. En el Atrahasis, la diosa madre mezcla arcilla con la carne y la sangre de un dios sacrificado para crear a los hombres, que trabajarán en lugar de los dioses. En el Enuma Elish, Ea crea a la humanidad con la sangre de Qingu, el jefe del ejército de Tiamat, con el mismo fin. En Gilgamesh, la diosa Aruru toma un pellizco de arcilla y lo arroja a la estepa, y de él nace Enkidu.",
 "pasajes": [
  ("genesis", "Génesis 2,7", "«Formó al hombre con polvo del suelo, e insufló en sus narices aliento de vida.»"),
  ("atrahasis", "Atrahasis, tablilla I", "Los dioses menores se rebelan contra el trabajo; la diosa madre crea al hombre con arcilla, carne y sangre."),
  ("enuma", "Enuma Elish, tablilla VI, 1–38", "Ea crea a la humanidad con la sangre de Qingu, para que sirva a los dioses."),
  ("gilgamesh", "Gilgamesh, tablilla I", "Aruru modela a Enkidu con un pellizco de arcilla."),
 ],
 "obras": [("genesis", "01"), ("genesis", "07"), ("atrahasis", "01"), ("atrahasis", "03"),
           ("enuma", "01"), ("enuma", "02")],
},
{
 "clave": "torre",
 "titulo": "La torre y el templo",
 "lema": "Ladrillo cocido para una torre que llegue al cielo, una casa para el dios: Babel, el Esagila de Marduk y el Tabernáculo del Éxodo.",
 "intro": "En el Génesis, los hombres cuecen ladrillos, usan betún como argamasa y empiezan una ciudad con una torre cuya cúspide llegue al cielo; Dios confunde su lengua y los dispersa, y la ciudad se llama Babel. En el Enuma Elish, los dioses pasan un año entero moldeando ladrillos para levantar a Marduk su casa en Babilonia, el Esagila, y alzan su cima. Las piezas de la colección muestran esa Babilonia real: la tablilla que da las medidas del templo y de su zigurat, el rey que lo reconstruye y la puerta por la que entraba la procesión de Marduk. En el Éxodo, Dios da a Moisés las medidas del Tabernáculo, un santuario que se monta y se desmonta en el desierto, y del arca con sus dos querubines; en el Levítico, Aarón y sus hijos son consagrados para servir en él.",
 "pasajes": [
  ("genesis", "Génesis 11,1–9", "La torre, la confusión de las lenguas y la dispersión de los hombres."),
  ("enuma", "Enuma Elish, tablilla VI, 55–75", "Los dioses fabrican ladrillos durante un año y construyen el Esagila para Marduk."),
  ("exodo", "Éxodo 25–27", "Las medidas del Tabernáculo y del arca de la alianza, con sus dos querubines."),
  ("levitico", "Levítico 8–9", "La consagración de Aarón y de sus hijos, y la primera ofrenda en el Tabernáculo."),
 ],
 "obras": [("genesis", "05"), ("genesis", "09"), ("enuma", "06"), ("enuma", "08"), ("enuma", "03"),
           ("enuma", "05"), ("exodo", "13"), ("levitico", "01")],
},
{
 "clave": "monstruos",
 "titulo": "Monstruos vencidos",
 "lema": "El guardián del bosque, el toro del cielo, el dragón de las aguas: el héroe contra el monstruo en Mesopotamia.",
 "intro": "En Gilgamesh, el héroe y Enkidu matan a Humbaba, el guardián que Enlil puso en el Bosque de los Cedros, y después al Toro del Cielo que Ishtar lanza contra Uruk. En el Enuma Elish, Marduk se enfrenta a Tiamat y a los once monstruos que ella engendró, la parte en dos y hace con su cuerpo el cielo y la tierra; a los monstruos no los destruye: los captura. En el Atrahasis el monstruo no se vence sino que se admite: al final del poema los dioses dejan entre los hombres a la «exterminadora» que arrebata a los niños.",
 "pasajes": [
  ("gilgamesh", "Gilgamesh, tablillas II–V", "El viaje al Bosque de los Cedros y la muerte de Humbaba."),
  ("gilgamesh", "Gilgamesh, tablilla VI", "Ishtar, rechazada, lanza contra Uruk al Toro del Cielo."),
  ("enuma", "Enuma Elish, tablillas I–IV", "Tiamat engendra once monstruos; Marduk la vence y los captura."),
  ("atrahasis", "Atrahasis, tablilla III", "Los límites que se ponen a la humanidad después del Diluvio, entre ellos la pāšittu."),
 ],
 "obras": [("gilgamesh", "03"), ("gilgamesh", "04"), ("gilgamesh", "02"), ("gilgamesh", "09"),
           ("gilgamesh", "11"), ("enuma", "03"), ("enuma", "09"), ("atrahasis", "05"), ("atrahasis", "06")],
},
{
 "clave": "duelo",
 "titulo": "El duelo",
 "lema": "El primer muerto de la humanidad y el amigo muerto del héroe: el llanto en el Génesis, la Ilíada y Gilgamesh.",
 "intro": "El Génesis cuenta el asesinato de Abel sin decir nada del dolor de sus padres. La Ilíada dedica sus últimos cantos al duelo: Aquiles por Patroclo, con los juegos fúnebres en su honor, y Príamo por Héctor, cuyo cuerpo va a pedir a Aquiles. En Gilgamesh, el héroe llora a Enkidu en la tablilla VIII. Los dos poemas usan la misma imagen: Aquiles gime como un león al que un cazador ha robado sus cachorros; Gilgamesh da vueltas como una leona que ha perdido los suyos. De la tablilla VIII no hay obra en la colección.",
 "pasajes": [
  ("genesis", "Génesis 4,1–16", "Caín mata a Abel."),
  ("iliada", "Ilíada XVIII, 22–35 y 316–322", "Aquiles se entera de la muerte de Patroclo; gime como un león al que han robado los cachorros."),
  ("iliada", "Ilíada XXIII", "Los funerales y los juegos en honor de Patroclo."),
  ("iliada", "Ilíada XXIV", "Príamo pide a Aquiles el cuerpo de Héctor; el llanto de Andrómaca."),
  ("gilgamesh", "Gilgamesh, tablilla VIII", "El lamento de Gilgamesh por Enkidu, como una leona que ha perdido sus cachorros."),
 ],
 "obras": [("genesis", "46"), ("genesis", "03"), ("genesis", "06"), ("iliada", "06"), ("iliada", "21"),
           ("iliada", "04"), ("iliada", "07"), ("iliada", "24"), ("iliada", "25")],
},
]
