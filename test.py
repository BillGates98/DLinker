from rdflib import Graph, Namespace, URIRef, Literal

# Créer un graphe RDF
g = Graph()

# Espace de noms RDF et OWL
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
owl = Namespace("http://www.w3.org/2002/07/owl#")

# Charger le fichier texte
with open('./validations/agrold/reference.txt', 'r') as file:
    for line in file:
        # Diviser la ligne en deux colonnes (séparées par une tabulation)
        columns = line.strip().split('\t')
        if len(columns) == 2:
            sujet, objet = columns
            # print(sujet, ' ----> ', objet)
            # Créer des URI pour le sujet et l'objet
            sujet_uri = URIRef(sujet)
            objet_uri = URIRef(objet)

            # Ajouter un triplet RDF avec le prédicat owl:sameAs
            g.add((sujet_uri, owl.sameAs, objet_uri))

# Écrire le graphe RDF dans un fichier RDF Turtle
g.serialize(destination='./validations/agrold/output.ttl', format='turtle')

print("Le fichier RDF a été généré avec succès.")


# import numpy as np

# # Supposons que votre matrice ressemble à ceci (c'est un exemple, adaptez-le à votre propre matrice) :
# matrice = np.array([[(5, 10), (15, 8), (7, 21)],[(6, 11), (5, 9), (3, 8)]])

# # Utilisez la fonction numpy.min avec axis=0 pour obtenir la valeur minimale de la première position de chaque tuple.
# #  for i in range(len(matrice[0]))
# valeur_minimale1 = np.min([ np.mean(matrice[:, 0]) ])
# valeur_minimale2 = np.min([ np.mean(matrice[:, 1]) ])

# # Affichez la valeur minimale.
# print("Valeur minimale de la première position :", valeur_minimale1, " valeur_minimale : ", valeur_minimale2)

# def ngram_similarity(str1, str2, N):
#     # Fonction pour extraire les n-grammes d'une chaîne de caractères.
#     def extract_ngrams(s, n):
#         ngrams = []
#         for i in range(len(s) - n + 1):
#             ngram = s[i:i + n]
#             ngrams.append(ngram)
#         return ngrams

#     # Extraction des n-grammes des deux chaînes.
#     ngrams1 = extract_ngrams(str1, N)
#     ngrams2 = extract_ngrams(str2, N)

#     # Calcul du nombre de n-grammes en commun.
#     common_ngrams = set(ngrams1) & set(ngrams2)

#     # Calcul de la similarité N-gram.
#     similarity = len(common_ngrams) / max(len(ngrams1), len(ngrams2))
#     similarity2 = len(common_ngrams) / (min(len(ngrams1), len(ngrams2)) - N + 1)
#     print('sim 2 : ', similarity2)
#     return similarity

# # Exemple d'utilisation :
# chaine1 = "bonjour"
# chaine2 = "bonsoir"
# N = 2
# similarity = ngram_similarity(chaine1, chaine2, N)
# print("Similarité N-gram :", similarity)


# def jaro_similarity(str1, str2):
#     # Fonction pour calculer la distance de Jaro-Winkler
#     def jaro_winkler_distance(s1, s2):
#         # Longueur des chaînes
#         len_s1 = len(s1)
#         len_s2 = len(s2)

#         # Longueur maximale pour la fenêtre de correspondance
#         max_len = max(len_s1, len_s2)

#         # Rayon de correspondance (distance maximale pour une correspondance)
#         match_distance = (max_len // 2) - 1

#         # Marqueurs de correspondance
#         s1_matches = [False] * len_s1
#         s2_matches = [False] * len_s2

#         # Nombre de correspondances
#         matches = 0

#         # Compter les correspondances
#         for i in range(len_s1):
#             start = max(0, i - match_distance)
#             end = min(i + match_distance + 1, len_s2)

#             for j in range(start, end):
#                 if not s2_matches[j] and s1[i] == s2[j]:
#                     s1_matches[i] = True
#                     s2_matches[j] = True
#                     matches += 1
#                     break

#         if matches == 0:
#             return 0.0

#         # Compter les transpositions
#         transpositions = 0
#         k = 0
#         for i in range(len_s1):
#             if s1_matches[i]:
#                 while not s2_matches[k]:
#                     k += 1
#                 if s1[i] != s2[k]:
#                     transpositions += 1
#                 k += 1

#         # Calculer la similarité de Jaro
#         jaro_similarity = (matches / len_s1 + matches / len_s2 + (matches - transpositions / 2) / matches) / 3.0

#         return jaro_similarity

#     # Calculer la distance de Jaro-Winkler
#     jaro_distance = 1.0 - jaro_winkler_distance(str1, str2)

#     return jaro_distance

# Exemple d'utilisation :
# chaine1 = "martha"
# chaine2 = "marhta"
# similarity = jaro_similarity(chaine1, chaine2)
# print("Similarité de Jaro :", similarity)
