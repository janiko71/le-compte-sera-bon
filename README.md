# Le compte sera bon

Algorithme de résolution du jeu "le compte est bon"

## Principe

Il s'agit de retrouver (calculer) un nombre compris entre 100 et 999, à partir de 6 nombres tirés aléatoirement parmi 24 plaques. Ces 6 nombres peuvent être combinés par des opérations arithmétiques. Les opérations autorisées sont donc l'addition, la soustraction, la multiplication et la division entière.

Tous les nombres de ce problème doivent être des entiers positifs, y compris les résultats intermédiaires.
 
Ce programme teste TOUTES les combinaisons possibles, donnant ainsi toutes les solutions. Si aucune solution n'est trouvée, on retourne la solution donnant le résultat le plus proche (qu'il soit supérieur ou inférieur au nombre recherché).

Sur mon PC ou sur mon smartphone, le temps d'exécution est de moins d'une seconde.

## Les 24 plaques

Parmi les 24 plaques, il y a les entiers de 1 à 10 (chacun étant en double exemplaire), soit 20 plaques. Les 4 dernières plaques sont 25, 50, 75, 100 (un seul exemplaire).

## Pourquoi ce programme ?

Au cours d'une discussion avec des collègues, au sujet des ordinateurs et de l'intelligence artificielle, j'avais lancé un exemple d'emploi détruit par les ordinateurs : celui (entre autres) de l'animateur [des Chiffres et des Lettres](https://fr.wikipedia.org/wiki/Des_chiffres_et_des_lettres) en charge du jeu le Compte est Bon.

En effet, pendant de très longues années, aucun ordinateur ne pouvait analyser **toutes** les combinaisons possibles pour être sûr de trouver une solution. Le problème était parfois résolu grâce à des optimisations de calculs, permettant de trouver _souvent_ une solution dans le temps imparti (40 secondes, pour les candidats), mais sans aucune assurance d'aboutir. 

Quant à la meilleure solution possible, c'est-à-dire la plus proche de la valeur recherchée, le problème était encore plus complexe car on ne peut être sûr de ne pas avoir de solution qu'après avoir examiné toutes les combinaisons possibles, et la meilleure solution ne peut apparaître qu'une fois avoir épuisé toutes les solutions.

Donc, par défi, j'ai voulu voir comment résoudre le problème et surtout en combien de temps. L'algorithme n'est pas spécialement optimisé, mais il tourne sur un smartphone, en Python, en moins d'une seconde... Un problème à la combinatoire de ce niveau, impossible à résoudre rapidement il y a encore quelques années, et aujourd'hui largement à la portée de mon smartphone.
