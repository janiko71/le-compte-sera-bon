#
#  ----------
#
#  Recherche de solution pour "le compte est bon" (jeu télévisé "des chiffres et des lettres")
#
#  ----------
#
#  Il s'agit de retrouver (calculer) un nombre compris entre 100 et 999, à partir de 6 nombres tirés aléatoirement parmi 24 
#  plaques*. Ces 6 nombres peuvent être combinés par des opérations arithmétiques. Les opérations autorisées sont donc 
#  l'addition, la soustraction, la multiplication et la division entière.
#
#  Tous les nombres de ce problème doivent être des entiers positifs, y compris les résultats intermédiaires.
# 
#  Ce programme teste TOUTES les combinaisons possibles, donnant ainsi toutes les solutions. Si aucune solution n'est trouvée,
#  on retourne la solution donnant le résultat le plus proche (qu'il soit supérieur ou inférieur au nombre recherché).
#
#  * Parmi les 24 plaques, il y a les entiers de 1 à 10 (chacun étant en double exemplaire), soit 20 plaques.
#    Les 4 dernières plaques sont 25, 50, 75, 100 (un seul exemplaire).
#
#

import io, os, sys, time
import re
import copy

import random

#
# Quelques globales...
#

nombre_a_trouver_test = random.randrange(100, 999)
plaques = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 25, 50, 75, 100]
tirage_test = []
for i in range(0,6):
    lg = len(plaques)
    rg = random.randrange(0, lg)
    tirage_test.append(plaques[rg])
    plaques.remove(plaques[rg])

global nb_combinaisons_testees
nb_combinaisons_testees = 0

global limite
limite = 1000

#
#    Classe des noeuds de recherche
#
#    Un noeud est un chemin (exclusif) de recherche. Chaque noeud peut avoir des descendants,
#    chacun étant une possibilité de choix.
#

class Nombre:
    
    #-----------------------------------------
    def __init__(self, valeur, chemin):
    #-----------------------------------------

        """
            Constructeur d'un Nombre
        """

        # On mémorise le nombre lui-même (entier positif)

        self.val  = valeur
        self.chemin = chemin


    #-----------------------------------------
    def __repr__(self):
    #-----------------------------------------

        """
            Affichage de la représentation du nombre (on affiche le nombre ainsi que la façon de le calculer)
        """

        # On affiche le nombre et son "chemin", à savoir la façon de le calculers+

        return "{} = ({})".format(self.val, self.chemin)


    #-----------------------------------------
    def identique(self, nb):
    #-----------------------------------------

        """
            Indique si deux 'Nombre's sont identiques ou pas
        """

        if (self.val != nb.val):
            return False
        elif (self.chemin != nb.chemin):
            return False
        else:
            return True


def remove_nombre(liste, nombre):

    for elem in liste:
        if elem.identique(nombre):
            liste.remove(elem)
    return


# --------------------------------------------------------------
def combinaisons_possibles(liste_nombres, nb_a_trouver):
# --------------------------------------------------------------

    global limite

    liste = []

    #
    # Boucle d'arrêt de la récursion : liste de longueur 2
    #

    if (len(liste_nombres) == 2):
        
        nombre_a = liste_nombres[0]
        nombre_b = liste_nombres[1]

        a = nombre_a.val
        b = nombre_b.val

        # Test addition
        
        val = a + b
        chemin = "({} + {})".format(nombre_a.chemin, nombre_b.chemin)
        if (val < limite):
            liste.append(Nombre(val, chemin))
            #liste.append(Nombre(val, a, b, '+'))

        # Test multiplication
        
        if (a != 1) and (b !=1):
            val = a * b
            chemin = "({} x {})".format(nombre_a.chemin, nombre_b.chemin)
            if (val < limite):
                liste.append(Nombre(val, chemin))
                #liste.append(Nombre(val, a, b, '+'))

        # Test soustraction
        
        if (a > b):
            val = a - b
            chemin = "({} - {})".format(nombre_a.chemin, nombre_b.chemin)
            liste.append(Nombre(val, chemin))
            #liste.append(Nombre(val, a, b, '+'))
        elif (b > a):
            val = b - a
            chemin = "({} - {})".format(b, a)
            liste.append(Nombre(val, chemin))
            #liste.append(Nombre(val, a, b, '+'))

        # Test division
        
        if (b > 1) and (a >= b) and (a % b == 0):
            val = a // b
            chemin = "({} : {})".format(nombre_a.chemin, nombre_b.chemin)
            liste.append(Nombre(val, chemin))
            #liste.append(Nombre(val, a, b, '+'))
            
        if (a > 1) and (b > a) and (b % a == 0):
            val = b // a
            chemin = "({} : {})".format(nombre_a.chemin, nombre_b.chemin)
            liste.append(Nombre(val, chemin))
            #liste.append(Nombre(val, a, b, '+'))

    #
    # Cas général (longueur de liste > 2)
    #

    n = len(liste_nombres)

    for nb in liste_nombres:

        copie_liste = copy.deepcopy(liste_nombres)
        remove_nombre(copie_liste, nb)
        liste_int = combinaisons_possibles(copie_liste, nb_a_trouver)
        for elem in liste_int:
            liste_comb_int = combinaisons_possibles([elem, nb], nb_a_trouver)
            liste = liste + liste_comb_int
            pass

    return liste
            
#
#  Idée de l'algo de recherche
#
#  On prend 2 nombres, et on cherche toutes les combinaisons possibles entre eux.
#  Chaque combinaison est un noeud de recherche.
#
#  Pour chaque noeud (combinaison), on dispose de :
#   - Valeur de la combinaison, et opération utilisée. Ex : (4,3,+) donne 12 en valeur
#   - On va calculer ensuite toutes les combinaisons pour les nombres restants, qui formeront
#     les noeuds "fils" du noeud en cours d'examen (récursion)
#   - Une fois cette liste établie, on calcule tous les résultats atteignables avec la valeur de
#     ce noeud combinés avec un des nombres de la liste des "fils"

def recherche_solution(liste_tirage, nb_a_trouver):

    liste = copy.deepcopy(liste_tirage)
    lc = combinaisons_possibles(liste, nb_a_trouver)
    print("Nombre de combinaisons testées : " + str(len(lc)))
    distance_solution = 999
    meilleure_solution = None
    liste_solutions = []
    for elem in lc:
        d = abs(nb_a_trouver - elem.val)
        if (d < distance_solution):
            distance_solution = d
            meilleure_solution = elem
        if d == 0:
            liste_solutions.append(elem)

    return liste_solutions, meilleure_solution, len(lc)
        
          


# =================================================================================================================
#
# Saisie des valeurs du tirage (plaques) et lancement de la recherche
#
# =================================================================================================================

c = input("Entrez les 6 nombres du tirage (plaques) : ")

if c == "":
    tirage = tirage_test
else:
    tirage = re.split('[, :;/]', c)

# On trie le tirage
# Très important !
# Dans l'algo général, on aura toujours b >= a
tirage.sort()

# Création de la liste initiale (= liste des nombres du tirage)
# ----

liste_tirage = []

for elem in tirage:
    try:
        liste_tirage.append(Nombre(int(elem), elem))
    except ValueError as e:
        print("Une des valeurs en entrée n\'est pas numérique : {}.".format(elem))
        exit(1)

#
# Saisie du nombre à chercher
#

d = input("Entrez le nombre à trouver : ")

if d == "":
    nombre_a_trouver = nombre_a_trouver_test
else:
    nombre_a_trouver = int(d)

#
#  Affichage du tirage
#

print('\nNombre à trouver : {}'.format(nombre_a_trouver))
str_tirage = "Tirage :"
for elem in liste_tirage:
    str_tirage = str_tirage + " " + str(elem)
print(str_tirage)
print()

#
#
# Recherche de solution : lecture des données et lancement de la recherche
#
#  

# Heure de démarrage
# ----

t0 = time.time()

# Lancement de la recherche (récursive)
# ----

solutions, meilleure_solution, nbc = recherche_solution(liste_tirage, nombre_a_trouver)
#recherche_solution([2, 4, 10], nombre_a_trouver)
#recherche_solution(liste_tirage, nombre_a_trouver)


if (len(solutions) > 0):
    # On a au moins une solution
    for elem in solutions:
        print(elem)
else:
    # Sinon on affiche la valeur la plus proche trouvée
    print("Solution la plus proche trouvée : {}".format(meilleure_solution))

str_nb = "{:,}".format(nbc)
str_nb = str_nb.replace(","," ")

# Fin d'exécution et affichage durée de la recherche
# ----

t1 = time.time()

print("\nDurée de la recherche : {:.2f} sec, avec {} combinaisons testées.\n".format(t1 - t0, str_nb))
