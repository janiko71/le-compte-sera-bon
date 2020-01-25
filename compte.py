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
    
global distance_solution
distance_solution = 999

global meilleure_solution
meilleure_solution = None

global liste_solutions
liste_solutions = []

global nb_a_trouver

global nb_combinaisons_testees
nb_combinaisons_testees = 0

global limite
limite = 1000

global t0

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

        #return "{}".format(self.val)
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


# --------------------------------------------------------------
def ajoute_nombre(liste, nombre):
# --------------------------------------------------------------

    global distance_solution
    global meilleure_solution
    global nb_a_trouver
    
    liste.append(nombre)
    
    distance = abs(nombre.val - nb_a_trouver)
    if (distance < distance_solution):
        distance_solution = distance
        meilleure_solution = copy.deepcopy(nombre)
        print("Meilleure solution trouvée : {}, nombre de combinaisons testées : {}".format(meilleure_solution, nb_combinaisons_testees), end="\r", flush=True)
    if (distance == 0):
        meilleure_solution = copy.deepcopy(nombre)
        liste_solutions.append(meilleure_solution)
        if (distance_solution > 0):
            print("Première solution trouvée : {} en {:.2f} sec, nombre de combinaisons testées : {}".format(meilleure_solution, time.time() - t0, nb_combinaisons_testees), end="\r", flush=True)
        else:
            distance_solution = 0

# --------------------------------------------------------------
def remove_nombre(liste, nombre):
# --------------------------------------------------------------

    for elem in liste:
        if elem.identique(nombre):
            liste.remove(elem)
    return


# --------------------------------------------------------------
def liste_combinaisons_2_nombres(nombre_a, nombre_b):
# --------------------------------------------------------------

    global limite
    global nb_a_trouver
    global nb_combinaisons_testees

    liste = []

    a = nombre_a.val
    b = nombre_b.val

    # Test addition
    
    val = a + b
    nb_combinaisons_testees = nb_combinaisons_testees + 1
    chemin = "({} + {})".format(nombre_a.chemin, nombre_b.chemin)
    if (val < limite):
        ajoute_nombre(liste, Nombre(val, chemin))
        liste.append(Nombre(val, chemin))
        #liste.append(Nombre(val, a, b, '+'))

    # Test multiplication
    
    if (a != 1) and (b !=1):
        val = a * b
        nb_combinaisons_testees = nb_combinaisons_testees + 1
        chemin = "({} x {})".format(nombre_a.chemin, nombre_b.chemin)
        if (val < limite):
            liste.append(Nombre(val, chemin))
            #liste.append(Nombre(val, a, b, '+'))

    # Test soustraction
    
    if (a > b):
        val = a - b
        nb_combinaisons_testees = nb_combinaisons_testees + 1
        chemin = "({} - {})".format(nombre_a.chemin, nombre_b.chemin)
        liste.append(Nombre(val, chemin))
        #liste.append(Nombre(val, a, b, '+'))
    """   
    elif (b > a):
        val = b - a
        chemin = "({} - {})".format(b, a)
        liste.append(Nombre(val, chemin))
        #liste.append(Nombre(val, a, b, '+'))
    """

    # Test division
    
    if (b > 1) and (a >= b) and (a % b == 0):
        val = a // b
        nb_combinaisons_testees = nb_combinaisons_testees + 1
        chemin = "({} : {})".format(nombre_a.chemin, nombre_b.chemin)
        liste.append(Nombre(val, chemin))
        #liste.append(Nombre(val, a, b, '+'))

    """    
    if (a > 1) and (b > a) and (b % a == 0):
        val = b // a
        chemin = "({} : {})".format(nombre_b.chemin, nombre_a.chemin)
        liste.append(Nombre(val, chemin))
        #liste.append(Nombre(val, a, b, '+'))
    """

    return liste


# --------------------------------------------------------------
def combinaisons_possibles(liste_nombres):
# --------------------------------------------------------------

    global limite
    global nb_a_trouver

    #
    # Boucle d'arrêt de la récursion : liste de longueur 1 ou 2
    #

    n = len(liste_nombres)

    liste = []

    if (n == 1):

        liste = []
        liste.append(liste_nombres[0])

    elif (n == 2):
        
        nombre_a = liste_nombres[0]
        nombre_b = liste_nombres[1]

        liste = copy.deepcopy(liste_combinaisons_2_nombres(nombre_a, nombre_b))

    else:

        #
        # Cas général (longueur de liste > 1)
        #

        # On combine le nombre examiné avec chacun des nombres possibles avec les nombres restants
        # On combine aussi le nombre examiné avec un des nombres du tirage
        # Pour chaque combinaison entre le nombre examiné et nombre du tirage, on va les combiner
        # avec chacun des nombres possibles avec les nombres restants 

        for nombre_a in liste_nombres:

            liste_nb_restants = copy.deepcopy(liste_nombres)
            remove_nombre(liste_nb_restants, nombre_a)

            # On teste la combinaison entre nombre_a et les autres nombres de la liste

            for nombre_b in liste_nb_restants:

                lr2 = copy.deepcopy(liste_combinaisons_2_nombres(nombre_a, nombre_b))
                liste = liste + lr2

                # Maintenant il faut combiner chaque liste 'lr' avec l'ensemble des combinaisons des nombres restants

                for elem in lr2:

                    liste_param = copy.deepcopy(liste_nombres)
                    remove_nombre(liste_param, nombre_a)
                    remove_nombre(liste_param, nombre_b)
                    liste_param.append(elem)

                    lr3 = combinaisons_possibles(liste_param)
                    liste = liste + lr3

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

def recherche_solution(liste_tirage):

    global nb_a_trouver

    liste = copy.deepcopy(liste_tirage)
    lc = combinaisons_possibles(liste)
    print("Nombre de combinaisons testées : " + str(len(lc)))
    f = open("log.txt","w")
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
    f.close()

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
######tirage.sort()

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
    nb_a_trouver = nombre_a_trouver_test
else:
    nb_a_trouver = int(d)

#
#  Affichage du tirage
#

print('\nNombre à trouver : {}'.format(nb_a_trouver))
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
solutions, meilleure_solution, nbc = recherche_solution(liste_tirage)
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
