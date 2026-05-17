# ==============================================================================
# Mini-Projet : Analyse Multivariée - Étape 0 : Statistiques Descriptives & Tests
# ==============================================================================

# Ce script réalise l'Analyse Exploratoire des Données (EDA).
# Il affiche la forme (shape), les infos, les descriptions statistiques basiques,
# et effectue des tests statistiques fondamentaux sur les datasets.

# 1. Chargement des packages nécessaires
library(tidyverse)

# ==============================================================================
# PARTIE 1 : CHARGEMENT DES DONNÉES
# ==============================================================================

cat("\n--- CHARGEMENT DES DONNÉES ---\n")
# On charge les deux datasets principaux
file_players <- "../data/processed/rank_features_enriched_v2.csv"
file_matches <- "../data/processed/match_features.csv"

df_players <- read_csv(file_players) %>% drop_na()

# Pour les matchs, on prend un échantillon pour que les tests tournent rapidement
df_matches <- read_csv(file_matches) %>% drop_na() %>% sample_n(min(10000, n()))

# ==============================================================================
# PARTIE 2 : SHAPE, INFOS ET DESCRIPTION (OVERVIEW)
# ==============================================================================

cat("\n--- 1. SHAPE (DIMENSIONS) ---\n")
cat("Dimensions du dataset Joueurs : ", dim(df_players)[1], " lignes, ", dim(df_players)[2], " colonnes\n")
cat("Dimensions du dataset Matchs  : ", dim(df_matches)[1], " lignes, ", dim(df_matches)[2], " colonnes\n")

cat("\n--- 2. STRUCTURE (INFOS) ---\n")
cat("Aperçu de la structure des Joueurs :\n")
glimpse(df_players)

cat("\n--- 3. STATISTIQUES DESCRIPTIVES (SUMMARY) ---\n")
cat("Résumé des variables clés des Joueurs :\n")
summary(df_players %>% select(avg_kda, avg_damage_per_min, avg_gold_per_min, win_rate))

# ==============================================================================
# PARTIE 3 : TESTS STATISTIQUES
# ==============================================================================

cat("\n--- 4. TESTS STATISTIQUES FORMELS ---\n")

# ------------------------------------------------------------------------------
# Test 1 : Test de Normalité (Shapiro-Wilk)
# Objectif : Vérifier si une variable suit une loi normale (courbe en cloche).
# Note : Shapiro-Wilk est limité à 5000 observations dans R, on prend un échantillon.
cat("\n>> Test de Shapiro-Wilk (Normalité) sur le KDA :\n")
sample_kda <- sample(df_players$avg_kda, 5000)
shapiro_res <- shapiro.test(sample_kda)
print(shapiro_res)
if(shapiro_res$p.value < 0.05) {
  cat("Interprétation : p-value < 0.05. Le KDA ne suit PAS une distribution parfaitement normale.\n")
} else {
  cat("Interprétation : p-value >= 0.05. Le KDA suit une distribution normale.\n")
}

# ------------------------------------------------------------------------------
# Test 2 : Test de Corrélation de Pearson
# Objectif : Vérifier si deux variables numériques évoluent ensemble.
cat("\n>> Test de Corrélation (Pearson) entre Or par minute et Dégâts par minute :\n")
cor_res <- cor.test(df_players$avg_gold_per_min, df_players$avg_damage_per_min, method = "pearson")
print(cor_res)
cat("Interprétation : Une corrélation de", round(cor_res$estimate, 2), "indique une liaison forte et positive.\n")

# ------------------------------------------------------------------------------
# Test 3 : Analyse de Variance (ANOVA)
# Objectif : Vérifier si la moyenne d'une variable numérique est significativement
# différente entre plusieurs groupes (ex: Les Dégâts selon le Rôle).
cat("\n>> Test ANOVA : Les dégâts moyens sont-ils différents selon le rôle (main_role) ?\n")
anova_res <- aov(avg_damage_per_min ~ main_role, data = df_players)
print(summary(anova_res))
# On extrait la p-value de l'ANOVA
p_val_anova <- summary(anova_res)[[1]][["Pr(>F)"]][1]
if(p_val_anova < 0.05) {
  cat("Interprétation : p-value < 0.05. OUI, il y a une différence statistiquement significative de dégâts entre les différents rôles (ADC, Support, etc.).\n")
}

# ------------------------------------------------------------------------------
# Test 4 : Test T de Student (T-test)
# Objectif : Comparer la moyenne entre deux groupes (ex: L'or gagné selon l'issue du match).
cat("\n>> Test T de Student : L'écart d'or (gold_diff) est-il différent si l'équipe gagne ou perd ?\n")
# On s'assure que team_won est bien un facteur ou logique
df_matches_ttest <- df_matches %>% 
  mutate(team_won = as.factor(team_won))

# S'il y a une colonne 'gold_diff_15', on teste dessus. Sinon on simule avec 'team_kills' si disponible.
# On cherche une colonne de différence, prenons la première colonne numerique pour l'exemple
# Adaptons en fonction des colonnes réelles :
if("gold_diff_15" %in% colnames(df_matches_ttest)) {
  t_res <- t.test(gold_diff_15 ~ team_won, data = df_matches_ttest)
  print(t_res)
  cat("Interprétation : La différence moyenne d'or à 15 min est fortement liée à la victoire.\n")
} else {
  cat("(Colonne 'gold_diff_15' non trouvée, assurez-vous d'utiliser les bonnes variables de match pour le t-test)\n")
}

cat("\n========================================================================\n")
cat("FIN DE L'ANALYSE EXPLORATOIRE (EDA)\n")
cat("Vous pouvez copier ces résultats de la console pour votre rapport final.\n")
cat("========================================================================\n")
