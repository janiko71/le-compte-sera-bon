# Le compte sera bon

Algorithme de résolution du jeu "le compte est bon". S'il n'y a pas de solution exacte, la solution la plus proche est indiquée.

## Principe

Il s'agit de retrouver (calculer) un nombre compris entre 100 et 999, à partir de 6 nombres tirés aléatoirement parmi 24 plaques. Ces 6 nombres peuvent être combinés par des opérations arithmétiques. Les opérations autorisées sont donc l'addition, la soustraction, la multiplication et la division entière.

Tous les nombres de ce problème doivent être des entiers positifs, y compris les résultats intermédiaires.
 
Ce programme teste **toutes** les combinaisons possibles, donnant ainsi toutes les solutions. Si aucune solution n'est trouvée, on retourne la solution donnant le résultat **le plus proche** (qu'il soit supérieur ou inférieur au nombre recherché).

## Algorithme amélioré (compte_dp.py)

La version `compte_dp.py` utilise une **programmation dynamique sur sous-ensembles** pour éviter de recalculer les mêmes combinaisons. L'idée est de construire toutes les valeurs possibles pour chaque sous-ensemble de plaques, puis de combiner ces sous-ensembles pour former des ensembles plus grands.

### Représentation des sous-ensembles

On représente un sous-ensemble de plaques par un **bitmask** :

- si le bit `i` vaut 1, la plaque `i` est incluse
- exemple avec 4 plaques : `mask = 0b1011` signifie plaques `0, 1 et 3`

On stocke les résultats sous la forme :

- `dp[mask]` = dictionnaire `valeur -> {expressions}`
- chaque expression est une chaîne représentant le calcul

### Initialisation

Pour chaque plaque prise seule (`mask` avec un seul bit à 1), on sait déjà :

- valeur = la plaque
- expression = `"valeur"`

Ainsi, `dp[1 << i][tirage[i]] = {str(tirage[i])}`.

### Construction par partitions

Pour chaque `mask` (sous-ensemble non vide), on le **partitionne** en deux sous-ensembles non vides `A` et `B` :

- on parcourt tous les sous-masques `submask` de `mask`
- on pose `A = submask` et `B = mask ^ submask`
- on ne garde que les partitions où `A < B` pour éviter les doublons

Pour chaque valeur possible dans `dp[A]` et `dp[B]`, on combine les expressions.

### Combinaisons autorisées

Les opérations sont les 4 opérations classiques, avec les contraintes :

- **addition** : toujours autorisée, commutative
- **multiplication** : autorisée, commutative (on évite les multiplications triviales par 1)
- **soustraction** : uniquement si le résultat est positif
- **division entière** : uniquement si la division est exacte et positive

Chaque combinaison génère une nouvelle valeur et une ou plusieurs expressions.

### Réduction de symétries

Deux optimisations majeures limitent les doublons :

1) **Commutativité**  
   Pour `+` et `x`, on impose `a <= b`.  
   Ainsi, `a + b` et `b + a` ne sont pas calculés deux fois.

2) **Partitions en double**  
   Les partitions `A|B` et `B|A` sont équivalentes, on ne garde que `A < B`.

### Mémoïsation et accumulation des résultats

Chaque résultat est mémorisé dans `dp[mask]`.  
Ainsi, si un même sous-ensemble réapparaît, on réutilise immédiatement toutes ses valeurs calculées.

### Suivi de la meilleure solution

Le programme maintient à tout moment :

- la distance minimale à la cible
- la meilleure expression correspondante

Si une valeur exacte est atteinte, toutes les expressions exactes sont stockées.

### Heuristique optionnelle (cap)

Un **cap** (plafond) sur les valeurs intermédiaires peut être activé :

- `cap = None` : recherche exacte complète
- `cap = N` : on ignore les valeurs > N (plus rapide, mais non exhaustif)

### Résultat final

À la fin :

- si des solutions exactes existent : on les affiche toutes
- sinon : on affiche la valeur la plus proche et son expression

### Pseudo-code (résumé)

```text
dp[mask] = dict(value -> set(expr))

pour chaque plaque i:
  dp[1<<i][tirage[i]] = {str(tirage[i])}
  maj_best(tirage[i], str(tirage[i]))

pour mask de 1 à (1<<n)-1:
  si mask est un singleton: continuer
  pour chaque submask propre de mask:
    other = mask ^ submask
    si submask < other:
      pour chaque (a, ea) dans dp[submask]:
        pour chaque (b, eb) dans dp[other]:
          si a > b: échanger (a,ea) et (b,eb)
          combiner a,b via +,x,-,/
          ajouter chaque résultat à dp[mask]
          maj_best(valeur, expression)
          si valeur == cible: stocker solution exacte
```

### Complexité (intuition)

L'algorithme reste exponentiel, mais **beaucoup plus rapide** que la recherche brute :

- chaque sous-ensemble est calculé **une seule fois**
- les symétries supprimées réduisent fortement le nombre de combinaisons

En pratique, le calcul est très rapide pour 6 plaques, même sur une machine modeste.

## Les 24 plaques

Parmi les 24 plaques, il y a les entiers de 1 à 10 (chacun étant en double exemplaire), soit 20 plaques. Les 4 dernières plaques sont 25, 50, 75, 100 (un seul exemplaire).

## Exemples
### Exemple avec une solution
Tirage : 5 9 7 4 1 6

Nombre à trouver : 945

Solution : 945 = (5 x 9) x (7 - 4) x (6 + 1)

### Exemple sans solution exacte
Tirage : 2 2 3 4 6 10

Nombre recherché : 631

Meilleure solution possible : [630] = ((6 x 10) + 3) x ((2 x 4) + 2) 

## Pourquoi ce programme ?

Au cours d'une discussion avec des collègues, au sujet des ordinateurs et de l'intelligence artificielle, j'avais lancé un exemple d'emploi détruit par les ordinateurs : celui (entre autres) de l'animateur [des Chiffres et des Lettres](https://fr.wikipedia.org/wiki/Des_chiffres_et_des_lettres) en charge du jeu le Compte est Bon.

En effet, pendant de très longues années, aucun ordinateur ne pouvait analyser **toutes** les combinaisons possibles pour être sûr de trouver une solution. Le problème était parfois résolu grâce à des optimisations de calculs, permettant de trouver _souvent_ une solution dans le temps imparti (40 secondes, pour les candidats), mais sans aucune assurance d'aboutir. 

Quant à la meilleure solution possible, c'est-à-dire la plus proche de la valeur recherchée, le problème était encore plus complexe car on ne peut être sûr de ne pas avoir de solution qu'après avoir examiné toutes les combinaisons possibles, et la meilleure solution ne peut apparaître qu'une fois avoir épuisé toutes les solutions.

Donc, par défi, j'ai voulu voir comment résoudre le problème et surtout en combien de temps. L'algorithme n'est pas spécialement optimisé, mais il tourne sur un smartphone, en Python, en moins d'une seconde... Un problème à la combinatoire de ce niveau, impossible à résoudre rapidement il y a encore quelques années, et aujourd'hui largement à la portée de mon smartphone (à vérifier avec le nouvel algo).
