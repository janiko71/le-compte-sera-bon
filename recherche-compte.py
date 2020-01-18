#
#  ----------
#
#  Recherche de solution pour "le compte est bon" (jeu télévisé "des chiffres et des lettres")
#
#  ----------
#
#  Il s'agit de retrouver (calculer) un nombre compris entre 100 et 999, à partir de 6 nombres tirés aléatoirement parmi 24 
#  plaques *. Ces 6 nombres peuvent être combinés par des opérations arithmétiques. Les opérations autorisées sont donc 
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

#
# Quelques globales...
#

nombre_a_trouver_test = 945
tirage_test = [7, 6, 1, 4, 5, 9]
tirage_test = [5, 5, 5, 7, 7, 7]

# "Distance" = Ecart entre une solution en cours d'évaluation et le nombre cible. AU départ, elle est "infinie".
best_guess_dist = 999

# On garde la meilleure solution dans une variable globale, car elle ne peut être déterminée qu'après avoir évalué toutes les combinaisons possibles.
best_guess_nombre = None


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


#
#
#  Fonctions utiles à la recherche
#
#


#-----------------------------------------
def est_present(nombre, liste):
#-----------------------------------------

    """
        Détecte si un nombre est présent dans une liste d'éléments de type "Nombre"
        ==> Devenue inutile
    """

    for elem in liste:

        if elem.nb == nombre:
            return True
    
    return False


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
def ajoute_operation(liste, nb_a, nb_b, ope, inverse = False):
#-----------------------------------------

    """
        Fonction curciale pour la recherche

        On part d'une liste de nombres (ne contenant ni nb_a ni nb_b), à laquelle on ajoute
        un nouveau nombre créé par un opération sur nb_a et nb_b. 

        Pour des questions de gestion des objets, on les passe toujours dans le même ordre en paramètre : a puis b.
        Sinon les pointeurs s'emmêlent et on risque de flinguer l'algo. Par contre, pour - et /, il peut arriver 
        que l'opération soit inversée. Ex : on ajoute (b - a) ou (b / a).
    """

    if not inverse:
        val = "{} {} {}".format(nb_a.nb, ope, nb_b.nb)
    else:
        val = "{} {} {}".format(nb_b.nb, ope, nb_a.nb)

    # Le nouveau nombre est construit à partir des deux nombres 'nb_a' et 'nb_b' combinés par une opération

    new_nombre = Nombre(eval(val))

    # La longueur du chemin est la somme des chemins des deux nombres. 
    #
    # Exemple : si on a 31 = 25 + 6, et 11 = 7 + 4, et que l'opération est '+',
    #           on obtiendra 42 = 31 + 11 = (26 + 6) + (7 + 4). On a donc en réalité
    #           utilisé 4 nombres (= longueur du chemin).

    new_nombre.lg_chemin = nb_a.lg_chemin + nb_b.lg_chemin

    # On compose le chemin (= façon de calculer le nombre)

    if ope == "*":
        ope = "x"
    elif ope == "//":
        ope = "/"

    if not inverse:
        new_nombre.chemin = "({} {} {})".format(nb_a.chemin, ope, nb_b.chemin)
    else:
        new_nombre.chemin = "({} {} {})".format(nb_b.chemin, ope, nb_a.chemin)

    # Construction de la nouvelle liste, avec la nouvelle valeur, mais en retirant l'élément "nb_b"

    new_liste_nombres = copie_nombres(liste, nb_b)
    new_liste_nombres.append(new_nombre)

    return new_liste_nombres


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

    # On regarde si on a trouve la meilleure solution (jusqu'à présent)

    global best_guess_dist, best_guess_nombre

    # Pour cela on passe en revue tous les éléments de la liste de nombres qu'on évalue.

    for elem in liste_nb:

        # La distance est donc la valeur absolue de la différence entre le nombre actuel examiné et le nombre recherché

        dist = abs(elem.nb - nombre_a_trouver.nb)

        if (dist < best_guess_dist):
            # On a trouvé plus proche
            best_guess_nombre = Nombre(elem.nb, elem.chemin, elem.lg_chemin)
            best_guess_dist = dist

    # Algo général (récursif)

    if dist == 0:

        # On a trouvé une solution possible. On l'affiche.

        print(liste_nb)

        return True

    else:

        #
        # Cas général
        #

        # On parcourt la liste des nombres passés en paramètre.

        for _, nb_a in enumerate(liste_nb):
        
            #
            # nb_a (a) correspond au 1er nombre qu'on va utiliser. On le supprimede de la liste des nombres avec
            # lesquels on va essayer de le combiner (liste_b).
            #

            liste_b = copie_nombres(liste_nb, nb_a)

            trouve = False
            
            for _, nb_b in enumerate(liste_b):

                # A partir du nombre nb_a (a), on va essayer de lui appliquer les différentes opérations possibles 
                # à chacun des nombres de la liste des nombres restants (liste_b).

                a = nb_a.nb
                b = nb_b.nb

                #
                # Test addition
                # ---
                # On imagine que le nombre résultat ne doit pas être trop grand, mais ça n'est pas obligatoire
                #

                if (a + b) < 1200:

                    new_liste_nombres = ajoute_operation(liste_b, nb_a, nb_b, "+")
                    trouve = recherche_solution(new_liste_nombres, nombre_a_trouver)

                #
                # Test soustraction
                # ---
                # Le résultat doit rester positif, donc si (a - b) est négatif, on tester la soustraction (b - a)
                #

                #if not trouve:

                if (a - b) > 0:

                    new_liste_nombres = ajoute_operation(liste_b, nb_a, nb_b, "-")
                    trouve = recherche_solution(new_liste_nombres, nombre_a_trouver)

                elif (a - b) < 0:

                    new_liste_nombres = ajoute_operation(liste_b, nb_a, nb_b, "-", inverse = True)
                    trouve = recherche_solution(new_liste_nombres, nombre_a_trouver)

                #
                # Test multiplication
                # ---
                # On suppose que le résultat ne doit pas être trop grand, comme pour l'addition, mais ça n'est pas obligatoire.
                # Par contre on ne teste pas la multiplication si l'un des deux nombres est 1 (ça n'apporte rien à la recherche).
                #

                #if not trouve:

                if ((a * b) < 1200) and (a != 1) and (b != 1):

                    new_liste_nombres = ajoute_operation(liste_b, nb_a, nb_b, "*")
                    trouve = recherche_solution(new_liste_nombres, nombre_a_trouver)

                #
                # Test division (entière)
                # ---
                # On ne teste la division que si elle est possible (résultat entier).
                # Note : le résultat peut être 1 (ça peut servir, des fois)

                #if not trouve:

                if (b >= a):

                    if (a % b == 0) and (b != 1):

                        new_liste_nombres = ajoute_operation(liste_b, nb_a, nb_b, "//")
                        trouve = recherche_solution(new_liste_nombres, nombre_a_trouver)

                if (a < b):

                    if (b % a == 0) and (a != 1):

                        new_liste_nombres = ajoute_operation(liste_b, nb_a, nb_b, "//", inverse = True)
                        trouve = recherche_solution(new_liste_nombres, nombre_a_trouver)

            return trouve

 
#
# Saisie des valeurs du tirage (plaques)
#

c = input("Entrez les 6 nombres du tirzge (plaques) : ")

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
#
# Recherche de solution : lecture des données et lancement de la recherche
#
#  

# Heure de démarrage
# ----

t0 = time.time()

# Lancement de la recherche (récursive)
# ----

recherche_solution(liste_tirage, nombre_a_trouver)

if (best_guess_dist != 0):

    print("Solution la plus proche trouvée : {}".format(best_guess_nombre))


# Fin d'exécution et affichage durée de la recherche
# ----

t1 = time.time()

print("Durée de la recherche : {:.2f} sec.".format(t1 - t0))