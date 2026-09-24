# -*- coding: utf-8 -*-
"""Descarga el retrato de cada autor a Autores/<clave>.jpg.

Excepción deliberada a la regla de máxima resolución: estos retratos son ilustración de
la interfaz, no piezas de la colección. Se muestran a 168 px de alto en una tarjeta, así
que se piden a Commons ya reducidos a 640 px. Bajar treinta y ocho originales de decenas
de megapíxeles engordaría el repositorio y la página publicable sin que se notara nada.

El pie de cada imagen dice QUÉ es: autorretrato, retrato por otro pintor, fotografía o
efigie póstuma. De Exequias, Eufronio, Villalpando, Jörg Breu y los escultores del
Laocoonte no se conserva retrato, y eso se dice en vez de poner una obra suya haciéndola
pasar por su cara.
"""
import io, json, os, re, subprocess, sys, time, urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "Autores")
ANCHO = 640
os.makedirs(DESTINO, exist_ok=True)

# clave -> (archivo en Commons, pie honesto)
RETRATOS = {
 "miguel_angel": ("Michelangelo Daniele da Volterra (dettaglio).jpg", "Retrato por Daniele da Volterra"),
 "masaccio":     ("Masaccio Self Portrait.jpg", "Autorretrato, en la Capilla Brancacci"),
 "tiziano":      ("Vecellio di Gregorio Tiziano - autoritratto.jpg", "Autorretrato"),
 "bruegel":      ("Pieter Bruegel the Elder - The Painter and the Buyer, ca. 1566 - Google Art Project.jpg",
                  "«El pintor y el comprador», tenido por autorretrato"),
 "cormon":       ("Fernand Cormon 1910-15.jpg", "Fotografía, c. 1910"),
 "blake":        ("William Blake by Thomas Phillips.jpg", "Retrato por Thomas Phillips"),
 "turner":       ("Joseph Mallord William Turner auto-retrato.jpg", "Autorretrato"),
 "dore":         ("Photograph of Gustave Doré by Nadar, between 1856 and 1858.jpg", "Fotografía de Nadar"),
 "scorel":       ("Antonis Mor - Jan van Scorel (1495–1562), 1559-1560, LDSAL 338; Scharf XXXVIII.jpg",
                  "Retrato por Antonio Moro"),
 "watts":        ("George Frederic Watts by George Frederic Watts.jpg", "Autorretrato"),
 "danby":        ("Francis Danby.jpg", "Retrato de época"),
 "cole":         ("Thomascole2.jpg", "Retrato de época"),
 "cranach":      ("Lucas Cranach d. Ä. 063.jpg", "Autorretrato"),
 "durero":       ("Dürer Alte Pinakothek.jpg", "Autorretrato, Alte Pinakothek"),
 "caravaggio":   ("Bild-Ottavio Leoni, Caravaggio.jpg", "Retrato por Ottavio Leoni"),
 "rembrandt":    ("Rembrandt van Rijn - Self-Portrait - Google Art Project.jpg", "Autorretrato"),
 "rubliov":      ("Andrei Rublev (miniature, 16 c) detail.jpg", "Efigie póstuma, miniatura del siglo XVI"),
 "delacroix":    ("Autoportrait - Eugène Delacroix - Musée du Louvre Peintures RF 25.jpg", "Autorretrato"),
 "gauguin":      ("Paul Gauguin 1891.png", "Fotografía, 1891"),
 "corot":        ("Jean-Baptiste Camille Corot - autoportrait.jpg", "Autorretrato"),
 "velazquez":    ("Diego Velázquez Autorretrato 45 x 38 cm - Colección Real Academia de Bellas Artes de San Carlos - Museo de Bellas Artes de Valencia.jpg",
                  "Autorretrato"),
 "john_martin":  ("John Martin by Henry Warren.jpg", "Retrato por Henry Warren"),
 "bosco":        ("Jheronimus Bosch (cropped).jpg", "Efigie póstuma"),
 "rubens":       ("Sir Peter Paul Rubens - Portrait of the Artist - Google Art Project.jpg", "Autorretrato"),
 "poussin":      ("Nicolas Poussin 078.jpg", "Autorretrato"),
 "ribera":       ("Ribera - Self-portrait.jpg", "Autorretrato"),
 "bellini":      ("Portræt af den venezianske maler Giovanni Bellini.jpg", "Retrato de época"),
 "lemoyne":      ("FrancoisLemoyne.jpg", "Retrato de época"),
 "ingres":       ("Ingres, Self-portrait.jpg", "Autorretrato"),
 "david":        ("David Self Portrait.jpg", "Autorretrato"),
 "matsch":       ("Franz Matsch Selfportrait 1904 Belvedre Vienna.png", "Autorretrato, 1904"),
 "hamilton":     ("Gavin hamilton.jpg", "Retrato de época"),
 "ivanov":       ("Alexander Andreyevich Ivanov.jpg", "Retrato de época"),
 "tiepolo_g":    ("Tiepolo, Giovanni Battista - Fresken Treppenhaus des Würzburger Residenzschlosses, Szenen zur Apotheose des Fürstbischofs, Detail Giovanni Battista Tiepolo - 1750-1753.jpg",
                  "Autorretrato dentro del fresco de Wurzburgo"),
 "tiepolo_d":    ("Treppenhaus Würzburg, Detail Giovanni Domenico Tiepolo.jpg",
                  "Retratado por su padre en el fresco de Wurzburgo"),
 "van_dyck":     ("Sir Anthony van Dyck - Self-portrait.jpg", "Autorretrato"),
 "vernet":       ("Carle Vernet by Robert Lefevre.jpg", "Retrato por Robert Lefèvre"),
 "bouguereau":   ("Bouguereau Portrait du peintre 1895.jpg", "Autorretrato, 1895, en una reproducción de época en blanco y negro"),
 "behzad":       ("Portrait of miniaturist Bezahd, 1511-1534. Yildiz Library, Constantinople.jpg",
                  "Retrato por otro pintor, s. XVI, con su nombre inscrito — Biblioteca de Yıldız, Estambul"),
}

# De estos no se conserva retrato. No se pone nada en su lugar.
SIN_RETRATO = {"exekias", "eufronio", "villalpando", "breu", "laocoonte", "marianos"}


def url_reducida(archivo):
    """URL de la miniatura de Commons a ANCHO px, vía Special:FilePath."""
    return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
            + urllib.parse.quote(archivo.replace(" ", "_")) + f"?width={ANCHO}")


def main():
    nuevos = saltados = fallos = 0
    for clave, (archivo, _pie) in sorted(RETRATOS.items()):
        destino = os.path.join(DESTINO, clave + ".jpg")
        if os.path.exists(destino) and os.path.getsize(destino) > 5000:
            saltados += 1; continue
        r = subprocess.run(["curl", "-sL", "--max-time", "60",
                            "-H", "User-Agent: PinturasColeccion/1.0 (proyecto personal)",
                            "-w", "%{http_code}", "-o", destino, url_reducida(archivo)],
                           capture_output=True, text=True)
        codigo = r.stdout.strip()[-3:]
        tam = os.path.getsize(destino) if os.path.exists(destino) else 0
        if codigo != "200" or tam < 5000:
            print(f"  FALLO {codigo} ({tam} B)  {clave}  <- {archivo[:56]}")
            if os.path.exists(destino): os.remove(destino)
            fallos += 1
        else:
            print(f"  OK  {tam/1024:6.0f} KB  {clave}")
            nuevos += 1
        time.sleep(2)
    print(f"\n{nuevos} descargados · {saltados} ya estaban · {fallos} fallidos")
    print(f"sin retrato conocido: {', '.join(sorted(SIN_RETRATO))}")


if __name__ == "__main__":
    main()
