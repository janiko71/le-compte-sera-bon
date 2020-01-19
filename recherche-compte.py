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

# *******************************************
# PRB 
#
# Tirage : 672 avec 100, 75, 7, 5, 1, 3
# Ne trouve que 673 !!
#  673 = ((100 x 7) - ((1 + (75 + 5)) / 3))
# Or 672 = 100 x (5 + 1) + 75 - 3

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


#
#    Classe des nombres utilisés pour la recherche
#
#    Objectif : Mémoriser la façon dont on a calculé le nombre en question. S'il s'agit d'un nombre 
#               du tirage initial, alors le chemin associé au nombre est lui-même. 
#

class Nombre:
    
    #-----------------------------------------
    def __init__(self, nb, chemin = "", lg_chemin = 1):
    #-----------------------------------------

        """
            Constructeur d'un Nombre
        """

        # On mémorise le nombre lui-même (entier positif)

        self.nb = nb 

        # Le chemin est la façon de calculer le nombre en question (sous forme de texte). On garde aussi sa longueur (nombre de nombres utilisés).
    
        if chemin == "":

            # Par défaut, si le chemin fournit est vide, c'est qu'il s'agit d'un nombre issu du tirage.
            self.chemin = str(nb)
            self.lg_chemin = 1

        else:

            # Si un chemin est fourni, on le recopie
            self.chemin  = chemin
            self.lg_chemin = lg_chemin


    #-----------------------------------------
    def __repr__(self):
    #-----------------------------------------

        """
            Affichage de la représentation du nombre (on affiche le nombre ainsi que la façon de le calculer)
        """

        # On affiche le nombre et son "chemin", à savoir la façon de le calculers+

        return "[{}] = {} (lg:{})".format(self.nb, self.chemin, self.lg_chemin)



#    Classe des objets des nombres atteignables
#
#    Un nombre atteignable est une combinaison des nombres du tirage ou des valeurs intérmédiaires produites lors de la recherche.
#    On se servira d'une liste pour implémenter la recherche des valeurs possibles (et donc atteignables).
#

class NombreAtteignable:

    def __init__(self, valeur, nombres_restants = []):

        self.valeur = valeur
        self.nombres_restants = nombres_restants

    def possede_nombre_restants(self):

        return len(self.nombres_restants) == 0

    def __repr__(self):

        return "{} ; {}".format(self.valeur, self.nombres_restants)



#
#
#  Fonctions utiles à la recherche
#
#

#-----------------------------------------
def compose(nombre_a, nombre_b, operation, inverse = False):
#-----------------------------------------
        
    global nb_combinaisons_testees

    nb_combinaisons_testees = nb_combinaisons_testees + 1

    if not inverse:
        val = "{} {} {}".format(nombre_a.nb, operation, nombre_b.nb)
    else:
        val = "{} {} {}".format(nombre_b.nb, operation, nombre_a.nb)
        
    # Le nouveau nombre est construit à partir des deux nombres 'nb_a' et 'nb_b' combinés par une opération

    new_nombre = Nombre(eval(val))

    # La longueur du chemin est la somme des chemins des deux nombres. 
    #
    # Exemple : si on a 31 = 25 + 6, et 11 = 7 + 4, et que l'opération est '+',
    #           on obtiendra 42 = 31 + 11 = (26 + 6) + (7 + 4). On a donc en réalité
    #           utilisé 4 nombres (= longueur du chemin).

    new_nombre.lg_chemin = nombre_a.lg_chemin + nombre_b.lg_chemin

    # On compose le chemin (= façon de calculer le nombre)

    if operation == "*":
        operation = "x"
    elif operation == "//":
        operation = "/"

    if not inverse:
        new_nombre.chemin = "({} {} {})".format(nombre_a.chemin, operation, nombre_b.chemin)
    else:
        new_nombre.chemin = "({} {} {})".format(nombre_b.chemin, operation, nombre_a.chemin)

    return new_nombre   


#-----------------------------------------
def copie_nombres(nombres_disponibles, nombre):
#-----------------------------------------

    """
        Réalise une copie d'une liste de nombre, mais en supprimant le nombre passé en paramètre.
        
        Attention : il ne faut le supprimer qu'une fois, car il faut se rappeler que les nombres
                    de 1 à 10 peuvent être en double.

        La liste renvoyée en résultat est une COPIE de la liste initiale, pour éviter de modifier
        cette liste initiale, ce qui perturberait les boucles for et la récursion.
    """

    supprime = False

    new_liste = []

    # On parcourt la liste initiale et on en crée une copie, sauf pour l'élément en paramètre

    for elem in nombres_disponibles:

        if (elem.nb == nombre.nb) and (elem.chemin == nombre.chemin) and not supprime:

            # Pour l'élément en paramètre (nombre à supprimer), on ne fait rien
            # Attention : il ne faut le supprimer qu'une fois !
            supprime = True

        else:

            # Sinon on copie l'élément dans la liste renvoyée
            new_liste.append(Nombre(elem.nb, elem.chemin, elem.lg_chemin))

    return new_liste




#-----------------------------------------
def copie_liste(nombres_disponibles, nombre):
#-----------------------------------------

    """
        Réalise une copie d'une liste de nombre, mais en supprimant le nombre passé en paramètre.
        
        Attention : il ne faut le supprimer qu'une fois, car il faut se rappeler que les nombres
                    de 1 à 10 peuvent être en double.

        La liste renvoyée en résultat est une COPIE de la liste initiale, pour éviter de modifier
        cette liste initiale, ce qui perturberait les boucles for et la récursion.
    """

    supprime = False

    new_liste = []

    # On parcourt la liste initiale et on en crée une copie, sauf pour l'élément en paramètre

    for elem in nombres_disponibles:

        if (elem.nb == nombre.nb) and (elem.chemin == nombre.chemin) and not supprime:

            # Pour l'élément en paramètre (nombre à supprimer), on ne fait rien
            # Attention : il ne faut le supprimer qu'une fois !
            supprime = True

        else:

            # Sinon on copie l'élément dans la liste renvoyée
            new_liste.append(Nombre(elem.nb, elem.chemin, elem.lg_chemin))

    return new_liste



#-----------------------------------------
def recherche_solution(liste_nb, nombre_a_trouver):
#-----------------------------------------

    """
        Idée d'algorithme
        ===============================

        On part d'un nombre à trouver, et d'une liste de nombres disponibles.

        On applique une opération possible (+, -, x, /) avec un des nombres disponibles. Si le résultat est dans un des nombres
        disponibles restants, alors on a gagné !

        Sinon on relance un calcul avec le nouveau nombre à trouver et la liste diminuée de l'élément utilisé. S'il n'y a plus
        d'élément disponible, alors on est en echec. 

    """
    global t0

    liste_des_solutions = []

    meilleure_solution = None
    distance_meilleure_solution = 999

    liste_base_recherche = []

    # Construction du graphe des valeurs possibles

    # Initialisation du graphe

    for nombre in liste_nb:

        liste_nombre_restants = copie_nombres(liste_nb, nombre)
        liste_base_recherche.append(NombreAtteignable(nombre, liste_nombre_restants))

    # Recherche générale

    valeur_cree = True

    while (valeur_cree):

        valeur_cree = False

        for nombre_atteignable in liste_base_recherche:

            nombre_a = nombre_atteignable.valeur

            # On mémorise la meilleure solution

            distance = abs(nombre_a.nb - nombre_a_trouver.nb)

            if (distance < distance_meilleure_solution):

                # On a trouvé mieux
                distance_meilleure_solution = distance
                meilleure_solution = Nombre(nombre_a.nb, nombre_a.chemin, nombre_a.lg_chemin)
                print("Meilleure solution : {}".format(meilleure_solution), end="\r", flush=True)

            if distance == 0:

                # Ici, on a carrément trouvé une solution !
                solution = Nombre(nombre_a.nb, nombre_a.chemin, nombre_a.lg_chemin)
                liste_des_solutions.append(solution)

                # On l'affiche si c'est la 1ère
                if len(liste_des_solutions) == 1:
                    print("Première solution trouvée en {:.2f} sec. : {}\n".format(time.time() - t0, solution))


            # On va calculer toutes les possibilités avec les nombres restants, pour l'élément en cours d'examen

            for nombre_b in nombre_atteignable.nombres_restants:

                a = nombre_a.nb
                b = nombre_b.nb

                #
                # Test addition
                # ---
                # On imagine que le nombre résultat ne doit pas être trop grand, mais ça n'est pas obligatoire
                #

                if (a + b) < 1200:

                    # On crée un nouveau "noeud"

                    liste_nb_restants = copie_liste(nombre_atteignable.nombres_restants, nombre_b)
                    nouveau_nombre = compose(nombre_a, nombre_b, "+")
                    nb = NombreAtteignable(nouveau_nombre, liste_nb_restants)
                    liste_base_recherche.append(nb)
                    valeur_cree = True

                #
                # Test soustraction
                # ---
                # Le résultat doit rester positif, donc si (a - b) est négatif, on tester la soustraction (b - a)
                #

                if (a - b) > 0:

                    # On crée un nouveau "noeud"
                    
                    liste_nb_restants = copie_liste(nombre_atteignable.nombres_restants, nombre_b)
                    nouveau_nombre = compose(nombre_a, nombre_b, "-")
                    nb = NombreAtteignable(nouveau_nombre, liste_nb_restants)
                    liste_base_recherche.append(nb)
                    valeur_cree = True

                elif (a - b) < 0:

                    liste_nb_restants = copie_liste(nombre_atteignable.nombres_restants, nombre_b)
                    nouveau_nombre = compose(nombre_a, nombre_b, "-", inverse = True)
                    nb = NombreAtteignable(nouveau_nombre, liste_nb_restants)
                    liste_base_recherche.append(nb)
                    valeur_cree = True

                #
                # Test multiplication
                # ---
                # On suppose que le résultat ne doit pas être trop grand, comme pour l'addition, mais ça n'est pas obligatoire.
                # Par contre on ne teste pas la multiplication si l'un des deux nombres est 1 (ça n'apporte rien à la recherche).
                #

                if ((a * b) < 1200) and (a != 1) and (b != 1):

                    liste_nb_restants = copie_liste(nombre_atteignable.nombres_restants, nombre_b)
                    nouveau_nombre = compose(nombre_a, nombre_b, "*", inverse = True)
                    nb = NombreAtteignable(nouveau_nombre, liste_nb_restants)
                    liste_base_recherche.append(nb)
                    valeur_cree = True   

                #
                # Test division (entière)
                # ---
                # On ne teste la division que si elle est possible (résultat entier).
                # Note : le résultat peut être 1 (ça peut servir, des fois)

                if (b >= a):

                    if (a % b == 0) and (b != 1):

                        liste_nb_restants = copie_liste(nombre_atteignable.nombres_restants, nombre_b)
                        nouveau_nombre = compose(nombre_a, nombre_b, "//")
                        nb = NombreAtteignable(nouveau_nombre, liste_nb_restants)
                        liste_base_recherche.append(nb)
                        valeur_cree = True   

                if (a < b):

                    if (b % a == 0) and (a != 1):

                        liste_nb_restants = copie_liste(nombre_atteignable.nombres_restants, nombre_b)
                        nouveau_nombre = compose(nombre_a, nombre_b, "//", inverse = True)
                        nb = NombreAtteignable(nouveau_nombre, liste_nb_restants)
                        liste_base_recherche.append(nb)
                        valeur_cree = True   

            # On enlève le noeud qu'on vient d'examiner, sinon on tombe dans une boucle infinie...

            liste_base_recherche.remove(nombre_atteignable)


    return liste_des_solutions, meilleure_solution





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

# Création de la liste initiale (= liste des nombres du tirage)
# ----

liste_tirage = []

for elem in tirage:
    try:
        liste_tirage.append(Nombre(int(elem)))
    except ValueError as e:
        print("Une des valeurs en entrée n\'est pas numérique : {}.".format(elem))
        exit(1)

#
# Saisie du nombre à chercher
#

d = input("Entrez le nombre à trouver : ")

if d == "":
    nombre_a_trouver = Nombre(nombre_a_trouver_test)
else:
    nombre_a_trouver = Nombre(int(d))

#
#  Affichage du tirage
#

print('\nNombre à trouver : {}\n'.format(nombre_a_trouver.nb))
str_tirage = "Tirage :"
for elem in liste_tirage:
    str_tirage = str_tirage + " " + str(elem.nb)
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

solutions, meilleure_solution = recherche_solution(liste_tirage, nombre_a_trouver)

if (len(solutions) > 0):
    # On a au moins une solution
    for elem in solutions:
        print(elem)
else:
    # Sinon on affiche la valeur la plus proche trouvée
    print("Solution la plus proche trouvée : {}".format(meilleure_solution))

str_nb = "{:,}".format(nb_combinaisons_testees)
str_nb = str_nb.replace(","," ")

# Fin d'exécution et affichage durée de la recherche
# ----

t1 = time.time()

print("\nDurée de la recherche : {:.2f} sec, avec {} combinaisons testées.\n".format(t1 - t0, str_nb))
