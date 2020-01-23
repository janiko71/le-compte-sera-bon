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



#
#    Classe des objets des nombres atteignables
#
#    Un nombre atteignable est une combinaison des nombres du tirage ou des valeurs intérmédiaires produites lors de la recherche.
#    On se servira d'une liste pour implémenter la recherche des valeurs possibles (et donc atteignables).
#

class NombreAtteignable:

    def __init__(self, valeur, liste_nombres_utilises, liste_nombres_a_tester, chemin = ""):

        self.valeur = valeur
        self.nombres_utilises = liste_nombres_utilises
        self.nombres_a_tester = liste_nombres_a_tester
        if chemin == "":
            self.chemin = str(valeur)
        else:
            self.chemin = chemin


    def __repr__(self):

        if len(self.nombres_utilises) == 0:
            return "{}".format(self.valeur)
        else:
            return "{} ={}".format(self.valeur, self.chemin)


    def identique(self, nombre):

        # Renvoie 'True' si les nombres sont "identiques", à savoir qu'ils ont la même valeur et 
        # qu'ils ont été construits à partir de la même liste de nombres.

        if (self.valeur != nombre.valeur):
            return False
        elif (self.nombres_utilises != nombre.nombres_utilises):
            return False       
        elif (self.nombres_a_tester != nombre.nombres_a_tester):
            return False
        elif (self.chemin != nombre.chemin):
            return False
        else:
            return True


    #
    # Opérations sur les nombres atteignables (composition de deux nombres)
    #

    @staticmethod
    def addition(nombre_a, b: int):

        valeur = nombre_a.valeur + b
        liste_nombres_utilises = copy.deepcopy(nombre_a.nombres_utilises)
        liste_nombres_utilises.append(b)
        liste_nombres_utilises.sort()
        liste_nombres_restants = copy.deepcopy(nombre_a.nombres_a_tester)
        liste_nombres_restants.remove(b)
        chemin = "({} + {})".format(nombre_a.chemin, str(b))

        return NombreAtteignable(valeur, liste_nombres_utilises, liste_nombres_restants, chemin)

    @staticmethod
    def soustraction_ab(nombre_a, b: int):

        valeur = nombre_a.valeur - b
        liste_nombres_utilises = copy.deepcopy(nombre_a.nombres_utilises)
        liste_nombres_utilises.append(b)
        liste_nombres_utilises.sort()
        liste_nombres_restants = copy.deepcopy(nombre_a.nombres_a_tester)
        liste_nombres_restants.remove(b)
        chemin = "({} - {})".format(nombre_a.chemin, str(b))

        return NombreAtteignable(valeur, liste_nombres_utilises, liste_nombres_restants, chemin)

    @staticmethod
    def soustraction_ba(a: int, nombre_b):

        valeur = a - nombre_b.valeur
        liste_nombres_utilises = copy.deepcopy(nombre_b.nombres_utilises)
        liste_nombres_utilises.append(a)
        liste_nombres_utilises.sort()
        liste_nombres_restants = copy.deepcopy(nombre_b.nombres_a_tester)
        liste_nombres_restants.remove(a)
        chemin = "({} - {})".format(str(a), nombre_b.chemin, )

        return NombreAtteignable(valeur, liste_nombres_utilises, liste_nombres_restants, chemin)

    @staticmethod
    def multiplication(nombre_a, b: int):

        valeur = nombre_a.valeur * b
        liste_nombres_utilises = copy.deepcopy(nombre_a.nombres_utilises)
        liste_nombres_utilises.append(b)
        liste_nombres_utilises.sort()
        liste_nombres_restants = copy.deepcopy(nombre_a.nombres_a_tester)
        liste_nombres_restants.remove(b)
        chemin = "({} x {})".format(nombre_a.chemin, str(b))

        return NombreAtteignable(valeur, liste_nombres_utilises, liste_nombres_restants, chemin)

    @staticmethod
    def division_ab(nombre_a, b: int):

        valeur = nombre_a.valeur // b
        liste_nombres_utilises = copy.deepcopy(nombre_a.nombres_utilises)
        liste_nombres_utilises.append(b)
        liste_nombres_utilises.sort()
        liste_nombres_restants = copy.deepcopy(nombre_a.nombres_a_tester)
        liste_nombres_restants.remove(b)
        chemin = "({} x {})".format(nombre_a.chemin, str(b))

        return NombreAtteignable(valeur, liste_nombres_utilises, liste_nombres_restants, chemin)

    @staticmethod
    def division_ba(a:int, nombre_b):

        valeur = a // nombre_b.valeur
        liste_nombres_utilises = copy.deepcopy(nombre_b.nombres_utilises)
        liste_nombres_utilises.append(a)
        liste_nombres_utilises.sort()
        liste_nombres_restants = copy.deepcopy(nombre_b.nombres_a_tester)
        liste_nombres_restants.remove(a)
        chemin = "({} x {})".format(str(a), nombre_b.chemin)

        return NombreAtteignable(valeur, liste_nombres_utilises, liste_nombres_restants, chemin)


#-----------------------------------------
def ajoute_liste_recherche(liste_recherche, nb):
#-----------------------------------------

    # Ajoute un nombre dans la liste de recherche de solution
    #
    # On n'ajoute 'nb' que s'il ne s'agit pas d'un doublon. Un doublon est un nombre
    # qu'on a déjà dans la liste et utilisant les mêmes chiffres (peu importe les 
    # opérations et leur ordre).

    valeurs = []
    nb_restants = []
    for elem in liste_recherche:
        valeurs.append(elem.valeur)
        nb_restants.append(copy.deepcopy(elem.nombres_a_tester))

    if not (nb.valeur in valeurs):
        # La valeur du nombre n'est pas dans la liste, c'est forcément un nouveau nombre
        liste_recherche.append(nb)
        return True
    elif not (nb.nombres_a_tester in nb_restants):
        # La valeur existe déjà, mais elle a été trouvée à partir de nombres différents, donc on l'ajout
        liste_recherche.append(nb)
        return True
    else:
        # La valeur a été trouvée, et elle a été construite avec les mêmes nombres (peu importantes les variantes
        # et les opérations utilisées), alors on ne rajoute pas ce nombre dans la liste, pour optimiser la recherche.
        return False


#-----------------------------------------
def recherche_solution(liste_recherche, nombre_a_trouver):
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

    nb_combinaisons_testees = 0

    meilleure_solution = None
    distance_meilleure_solution = 999
    temps_solution = 0.0

    # Recherche générale

    valeur_cree = True

    while (valeur_cree):

        valeur_cree = False

        new_liste_recherche = []

        for nombre_a in liste_recherche:

            # On examine toutes les possibilités pour 'nombre_a'. Donc on peut le retirer de la liste
            # servant de base à la recherche 
            
            # On fait une copie de la liste de recherche, en excluant l'élément en cours

            valeur = nombre_a.valeur

            # On mémorise la meilleure solution

            distance = abs(valeur - nombre_a_trouver)

            if (distance < distance_meilleure_solution):

                # On a trouvé mieux
                distance_meilleure_solution = distance
                meilleure_solution = NombreAtteignable(nombre_a.valeur, [], [], nombre_a.chemin)

            if distance == 0:

                # Ici, on a carrément trouvé une solution !
                solution = NombreAtteignable(nombre_a.valeur, [], [], nombre_a.chemin)
                liste_des_solutions.append(solution)

                # On mémorise le temps mis pour trouver la 1ère solution
                if len(liste_des_solutions) == 1:
                    temps_solution = time.time() - t0

            # On affiche l'avancement de la recherche, et la meilleure solution jusqu'à présent
            
            if (distance_meilleure_solution > 0):
                print("Meilleure solution : {} {}, nombre de combinaisons testées : {} ({})".format(meilleure_solution, meilleure_solution.chemin, nb_combinaisons_testees, len(liste_recherche)), end="\r", flush=True)
            else:
                print("Première solution : {} {}, trouvée en {:.2f} sec., nombre de combinaisons testées : {} ({})".format(meilleure_solution, meilleure_solution.chemin, temps_solution, nb_combinaisons_testees, len(liste_recherche)), end="\r", flush=True)


            # On va calculer toutes les possibilités avec les nombres restants (tous les nombres
            # sauf le nombre_a), pour l'élément en cours d'examen

            for nombre_b in nombre_a.nombres_a_tester:

                a = nombre_a.valeur
                b = nombre_b

                #
                # Test addition
                # ---
                # On imagine que le nombre résultat ne doit pas être trop grand, mais ça n'est pas obligatoire
                #
                    
                if (a + b) < 1200:

                    # On crée un nouveau "noeud"

                    nb_combinaisons_testees = nb_combinaisons_testees + 1

                    nb = NombreAtteignable.addition(nombre_a, nombre_b)
                    ajoute_liste_recherche(new_liste_recherche, nb)
                    valeur_cree = True

                #
                # Test soustractions
                # ---
                # Le résultat doit rester positif, donc si (a - b) est négatif, on tester la soustraction (b - a)
                #

                if a > b:

                    # On crée un nouveau "noeud"

                    nb_combinaisons_testees = nb_combinaisons_testees + 1

                    nb = NombreAtteignable.soustraction_ab(nombre_a, nombre_b)
                    ajoute_liste_recherche(new_liste_recherche, nb)
                    valeur_cree = True

                if b > a:

                    # On crée un nouveau "noeud"

                    nb_combinaisons_testees = nb_combinaisons_testees + 1

                    nb = NombreAtteignable.soustraction_ba(nombre_b, nombre_a)
                    ajoute_liste_recherche(new_liste_recherche, nb)
                    valeur_cree = True

                #
                # Test multiplication
                # ---
                # On suppose que le résultat ne doit pas être trop grand, comme pour l'addition, mais ça n'est pas obligatoire.
                # Par contre on ne teste pas la multiplication si l'un des deux nombres est 1 (ça n'apporte rien à la recherche).
                #

                if ((a * b) < 1200) and (a != 1) and (b != 1):

                    # On crée un nouveau "noeud"

                    nb_combinaisons_testees = nb_combinaisons_testees + 1

                    nb = NombreAtteignable.multiplication(nombre_a, nombre_b)
                    ajoute_liste_recherche(new_liste_recherche, nb)
                    valeur_cree = True

                #
                # Test division (entière)
                # ---
                # On ne teste la division que si elle est possible (résultat entier).
                # Note : le résultat peut être 1 (ça peut servir, des fois)

                if b > a:

                    if (b % a == 0) and (a != 1):

                        # On crée un nouveau "noeud"

                        nb_combinaisons_testees = nb_combinaisons_testees + 1

                        nb = NombreAtteignable.division_ba(b, nombre_a)
                        ajoute_liste_recherche(new_liste_recherche, nb)
                        valeur_cree = True

                if b < a:

                    if (a % b == 0) and (b != 1):

                        # On crée un nouveau "noeud"

                        nb_combinaisons_testees = nb_combinaisons_testees + 1

                        nb = NombreAtteignable.division_ab(nombre_a, b)
                        ajoute_liste_recherche(new_liste_recherche, nb)
                        valeur_cree = True

        liste_recherche = new_liste_recherche

        # On enlève aussi les doublons. 
        # Exemple de doublons : (2 x 2) + 3 et (2 + 2 + 3). Le résultat est 7, et on utilise les mêmes nombres.
        # Peu importe qu'il existe plusieurs façons d'arriver à 7, il suffit de garder une des façons de calculer...
        # Donc on considère qu'il y a un doublon quand on a plusieurs façons d'arriver au même résultat avec les mêmes 
        # nombres, mais des opérations différentes.

        pass

    print()

    return liste_des_solutions, meilleure_solution, nb_combinaisons_testees




# =================================================================================================================
#
# Saisie des valeurs du tirage (plaques) et lancement de la recherche
#
# =================================================================================================================

ch = input("Entrez les 6 nombres du tirage (plaques) : ")

if ch == "":
    tirage_str = tirage_test
else:
    tirage_str = re.split('[, :;/]', ch)

# On trie le tirage
# Très important !
# Dans l'algo général, on aura toujours b >= a
tirage = []
try:
    for elem in tirage_str:
        tirage.append(int(elem))
except ValueError as e:
    print("Une des valeurs en entrée n\'est pas numérique : {}.".format(elem))
    exit(1)

# Création de la liste initiale (= liste des nombres du tirage)
# ----

liste_tirage = []

for elem in tirage:

    nombres_utilises = []
    nombres_restants = copy.deepcopy(tirage) 
    nombres_restants.remove(elem)
    liste_tirage.append(NombreAtteignable(elem, nombres_utilises, nombres_restants))

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

print('\nNombre à trouver : {}\n'.format(nombre_a_trouver))
str_tirage = "Tirage :"
for elem in liste_tirage:
    str_tirage = str_tirage + " " + str(elem.valeur)
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

solutions, meilleure_solution, nb_comb = recherche_solution(liste_tirage, nombre_a_trouver)

if (len(solutions) > 0):
    # On a au moins une solution
    for elem in solutions:
        print("{} = {}".format(elem, elem.chemin))
else:
    # Sinon on affiche la valeur la plus proche trouvée
    print("Solution la plus proche trouvée : {} = {}".format(meilleure_solution, meilleure_solution.chemin))

str_nb = "{:,}".format(nb_comb)
str_nb = str_nb.replace(","," ")

# Fin d'exécution et affichage durée de la recherche
# ----

t1 = time.time()

print("\nDurée de la recherche : {:.2f} sec, avec {} combinaisons testées.\n".format(t1 - t0, str_nb))
