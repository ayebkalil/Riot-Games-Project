# ==============================================================================
# Mini-Projet : Analyse Multivariée - Décision Métier et Feature Engineering
# Scénario : Le problème des 10 Ranks vs 4 Groupes ELO
# ==============================================================================

# Ce script démontre une "Smart Decision" (Décision intelligente) prise lors
# de la préparation des données : réduire 10 classes très superposées en 4 
# classes plus distinctes pour améliorer les performances d'un modèle prédictif.

# Installer MASS si nécessaire : install.packages("MASS")
library(tidyverse)
library(FactoMineR)
library(factoextra)
library(ggridges)
library(MASS) # Pour l'Analyse Discriminante Linéaire (LDA) - Un classique multivarié !

# 1. Chargement des données
file_path <- "C:/Users/ayebk/OneDrive/Desktop/hezou/Riot Games Project/data/processed/rank_features_enriched_v2.csv"
df <- read_csv(file_path) %>% drop_na()

# ==============================================================================
# PARTIE 1 : LE PROBLÈME (Superposition massive avec 10 Ranks)
# ==============================================================================

# Sélection des variables clés pour la prédiction
features <- c("avg_kda", "avg_cs_per_min", "avg_gold_per_min", "avg_damage_per_min", "win_rate")

# A. Visualisation via ACP
# On projette les joueurs sur 2 dimensions et on colore par leurs 10 ranks.
res.pca <- PCA(df[, features], scale.unit = TRUE, graph = FALSE)

p1_pca <- fviz_pca_ind(res.pca, geom = "point", habillage = df$tier, 
                       addEllipses = TRUE, ellipse.level = 0.8, alpha.ind = 0.4) +
  labs(title = "PROBLÈME : Superposition totale des 10 Ranks",
       subtitle = "Impossible pour un modèle de tracer des frontières claires.") +
  theme_minimal()

print(p1_pca)

# B. Preuve Mathématique : Modèle LDA (Linear Discriminant Analysis)
# On tente d'entraîner un modèle multivarié pour prédire le rank exact (10 classes).
formule_10 <- as.formula(paste("tier ~", paste(features, collapse = " + ")))
lda_10 <- lda(formule_10, data = df)

# Calcul de l'accuracy (Précision) : Sera très faible !
pred_10 <- predict(lda_10)$class
acc_10 <- mean(pred_10 == df$tier)
cat("\n=== PERFORMANCE AVEC 10 RANKS ===\n")
cat("Précision de l'Analyse Discriminante Linéaire :", round(acc_10 * 100, 2), "%\n")


# ==============================================================================
# PARTIE 2 : LA DÉCISION "SMART" (Regroupement en 3 catégories ELO)
# ==============================================================================

# Fusion des groupes High et Elite
df_smart <- df %>%
  mutate(elo_group = case_when(
    tier %in% c("Iron", "Bronze", "Silver") ~ "1_Low_Elo",
    tier %in% c("Gold", "Platinum", "Emerald") ~ "2_Mid_Elo",
    tier %in% c("Diamond", "Master", "Grandmaster", "Challenger") ~ "3_High_Elite_Elo",
    TRUE ~ "Unknown"
  ))

# ==============================================================================
# PARTIE 3 : LA SOLUTION ET L'AMÉLIORATION
# ==============================================================================

# A. Nouvelle Visualisation via ACP
p2_pca <- fviz_pca_ind(
  res.pca,
  geom = "point",
  habillage = df_smart$elo_group,
  addEllipses = TRUE,
  ellipse.level = 0.8,
  alpha.ind = 0.4
) +
  labs(
    title = "SOLUTION : Clusters plus distincts avec 3 Groupes ELO",
    subtitle = "Fusion des groupes High et Elite pour réduire le chevauchement."
  ) +
  scale_color_manual(values = c("#FC4E07", "#E7B800", "#00AFBB")) +
  theme_minimal()

print(p2_pca)

# ==============================================================================
# B. Preuve Mathématique avec le nouveau modèle LDA
# ==============================================================================

formule_3 <- as.formula(
  paste("elo_group ~", paste(features, collapse = " + "))
)

lda_3 <- lda(formule_3, data = df_smart)

# Calcul de la nouvelle accuracy
pred_3 <- predict(lda_3)$class
acc_3 <- mean(pred_3 == df_smart$elo_group)

cat("\n=== PERFORMANCE AVEC 3 GROUPES ELO ===\n")
cat(
  "Précision de l'Analyse Discriminante Linéaire :",
  round(acc_3 * 100, 2),
  "%\n"
)

# ==============================================================================
# C. Density Plot
# ==============================================================================

p3_density <- ggplot(
  df_smart,
  aes(
    x = avg_cs_per_min,
    y = elo_group,
    fill = elo_group
  )
) +
  geom_density_ridges(alpha = 0.8) +
  scale_fill_manual(values = c("#FC4E07", "#E7B800", "#00AFBB")) +
  theme_minimal() +
  labs(
    title = "Séparation des statistiques après regroupement",
    subtitle = "Fusion des niveaux High et Elite",
    x = "CS par Minute",
    y = "Groupe ELO"
  )
print(p3_density)
