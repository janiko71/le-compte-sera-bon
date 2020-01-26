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

#tirage_test = [5, 100, 4, 7]
#nombre_a_trouver_test = 528
    
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
    def __init__(self, valeur, chemin, est_plaque = False):
    #-----------------------------------------

        """
            Constructeur d'un Nombre
        """

        # On mémorise le nombre lui-même (entier positif)

        self.val  = valeur
        self.chemin = chemin
        self.est_plaque = est_plaque


    #-----------------------------------------
    def __repr__(self):
    #-----------------------------------------

        """
            Affichage de la représentation du nombre (on affiche le nombre ainsi que la façon de le calculer)
        """

        # On affiche le nombre et son "chemin", à savoir la façon de le calculers+

        if self.est_plaque:
            return str(self.val)
        else:
            return "{} = ({})".format(self.val, self.chemin)


    #-----------------------------------------
    def identique(self, nb):
    #-----------------------------------------

        """
            Indique si deux 'Nombre's sont identiques ou pas, à partir des valeurs (propriétés) des objets concernés.

            Indispensable car les nombres traités sont des objets, ils ne sont donc considérés comme égaux que s'il s'agit
            du même objet en mémoire. Or on veut savoir si deux objets sont identiques si leurs valeurs (propriétés) sont 
            les mêmes ou pas.
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


    """
        On ajoute un nombre dans la liste passée en paramètre. 

        On en profite pour évaluer le nombre, c'est-à-dire voir s'il s'agit
        de la meilleure solution trouvée jusqu'à présent ou s'il s'agit d'une
        des solutions possibles. Dans ce cas, on mémorise toutes les solutions
        que l'on trouve.
    """

    global distance_solution
    global meilleure_solution
    global liste_solutions
    global nb_a_trouver
    global ts
    
    # Ajout dans la liste

    liste.append(nombre)
    
    #
    #  Vérification de la solution
    #

    distance = abs(nombre.val - nb_a_trouver)

    if (distance < distance_solution):

        # Ici on a fait mieux : l'écart avec le nombre à trouver est le plus petit trouvé jusqu'à présent

        if distance > 0:

            # Cas où on n'a pas une solution exacte, mais une solution approchée
            meilleure_solution = copy.deepcopy(nombre)


        else:

            # distance = 0... Bingo : on a trouvé une solution !
            ts = time.time()
            meilleure_solution = copy.deepcopy(nombre)
            liste_solutions.append(meilleure_solution)


        # La meilleure solution trouvée est donc maintenant à la distance examinée
        distance_solution = distance


# --------------------------------------------------------------
def remove_nombre(liste, nombre):
# --------------------------------------------------------------

    """ 
        Suppression d'un nombre dans une liste

        Comme la liste peut être une copie de la liste contenant initialement le nombre en parmaètre,
        on ne peut pas faire de test d'égalité directement car on pointe sur des objets. L'égalité est
        donc déterminée à partir des valeurs de 'nombre', et non de l'objet lui-même.
    """

    for elem in liste:
        if elem.identique(nombre):
            liste.remove(elem)
    return


# --------------------------------------------------------------
def liste_combinaisons_2_nombres(nombre_a, nombre_b):
# --------------------------------------------------------------

    """
        Cette fonction teste toutes les combinaisons possibles entre deux nombres, et renvoie la liste
        des nombres pouvant être produits avec ces deux nombres.

        Les nombres produits doivent être des entiers naturels positifs exclusivement.

        Exemples : 5 et 2 donneront 3 (5 -2), 7 (5 + 2), 10 (2 x 5) mais aucune division (5 / 2 n'est pas entier).

        On suppose qu'il y a une limite supérieure à ne pas dépasser (fixée à 1000), mais je ne sais pas
        si cette limite figure dans les règles du jeu. 
    """

    global limite
    global nb_a_trouver
    global nb_combinaisons_testees
    global distance_solution
    global meilleure_solution
    global liste_solutions
    global ts

    # Affichage intermédiaire, état de la recherche

    str_nb = "{:,}".format(nb_combinaisons_testees)
    str_nb = str_nb.replace(","," ")

    if (len(liste_solutions) == 0):
        str_aff = "Meilleure solution trouvée : {}, nombre de combinaisons testées : {}".format(meilleure_solution, str_nb) + " "*72
        print(str_aff, end="\r", flush=True)
    else:
        str_aff = "Première solution trouvée : {} en {:.2f} sec, nombre de combinaisons testées : {}".format(meilleure_solution, ts - t0, str_nb) + " "*72
        print(str_aff, end="\r", flush=True)

    # Début algo 

    liste = []

    a = nombre_a.val
    b = nombre_b.val

    # Test addition
    
    val = a + b
    nb_combinaisons_testees = nb_combinaisons_testees + 1
    if (val < limite) and (val != a) and (val != b):
        chemin = "({} + {})".format(nombre_a.chemin, nombre_b.chemin)
        ajoute_nombre(liste, Nombre(val, chemin))

    # Test multiplication
    
    if (a != 1) and (b !=1):
        val = a * b
        nb_combinaisons_testees = nb_combinaisons_testees + 1
        if (val < limite) and (val != a) and (val != b):
            chemin = "({} x {})".format(nombre_a.chemin, nombre_b.chemin)
            ajoute_nombre(liste, Nombre(val, chemin))

    # Test soustraction
    
    if (a > b):
        val = a - b
        nb_combinaisons_testees = nb_combinaisons_testees + 1
        if (val != a) and (val != b):
            chemin = "({} - {})".format(nombre_a.chemin, nombre_b.chemin)
            ajoute_nombre(liste, Nombre(val, chemin))

    # Test division
    
    if (b > 1) and (a >= b) and (a % b == 0):
        val = a // b
        nb_combinaisons_testees = nb_combinaisons_testees + 1
        if (val != a) and (val != b):
            chemin = "({} : {})".format(nombre_a.chemin, nombre_b.chemin)
            ajoute_nombre(liste, Nombre(val, chemin))


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
        liste_tirage.append(Nombre(int(elem), elem, True))
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
