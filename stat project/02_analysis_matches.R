# ==============================================================================
# Mini-Projet : Analyse Multivariée - Dynamique des Matchs (Match Features)
# ==============================================================================

# 1. Chargement des packages nécessaires
# Décommentez la ligne ci-dessous si des packages manquent :
# install.packages(c("tidyverse", "FactoMineR", "factoextra", "cluster", "corrplot", "ggridges"))
library(tidyverse)
library(FactoMineR)
library(factoextra)
library(cluster)
library(corrplot)
library(ggridges) # Pour les Ridge plots (Density plots superposés)

# ==============================================================================
# ÉTAPE 1 & 2 : Compréhension et Préparation des données "Smart"
# ==============================================================================

# Chemin vers le dataset
file_path <- "C:/Users/ayebk/OneDrive/Desktop/hezou/Riot Games Project/data/processed/match_features.csv"
df_matches <- read_csv(file_path)

df_clean <- drop_na(df_matches)

# DÉCISION SMART 1 : Échantillonnage justifié
# Avec >350 000 lignes, l'ACP et le Clustering sont gourmands en RAM.
# On prend un échantillon aléatoire de 10 000 matchs. Statistiquement, 
# la Loi des Grands Nombres garantit que 10 000 individus sont largement suffisants
# pour extraire les tendances globales de la population sans perte de précision.
set.seed(42)
df_sample <- df_clean %>% sample_n(10000)

# Sélection des variables quantitatives (différentiels)
df_quant <- df_sample %>%
  dplyr::select(
    gold_diff,
    damage_diff,
    kills_diff,
    deaths_diff,
    assists_diff,
    vision_diff,
    turrets_diff,
    dragons_diff,
    barons_diff
  )

cor_matrix <- cor(df_quant)
corrplot(cor_matrix, method = "color", type = "upper", tl.col = "black", 
         tl.srt = 45, main = "Corrélation des différentiels")


# ==============================================================================
# ÉTAPE 3 : Analyse Factorielle (ACP)
# ==============================================================================

res.pca <- PCA(df_quant, scale.unit = TRUE, ncp = 5, graph = FALSE)

fviz_eig(res.pca, addlabels = TRUE, ylim = c(0, 70), 
         main = "Scree plot : Domination du Premier Axe (Snowball)")

# DÉCISION SMART 2 : Biplot
# Montre la distribution des matchs selon les axes de victoire.
fviz_pca_biplot(
  res.pca,
  geom.ind = "point",
  fill.ind = "gray",
  col.ind = "black",
  alpha.ind = 0.1,
  col.var = "red",
  repel = TRUE,
  title = "Biplot : Dynamique globale des matchs"
)

# ==============================================================================
# ÉTAPE 4 : Classification (K-Means) Robuste
# ==============================================================================

df_scaled <- scale(df_quant)

# DÉCISION SMART 3 : Multiple méthodes pour trouver 'k'
# Comparaison Coude vs Silhouette
p1 <- fviz_nbclust(df_scaled, kmeans, method = "wss", k.max = 6) + labs(subtitle = "Coude")
p2 <- fviz_nbclust(df_scaled, kmeans, method = "silhouette", k.max = 6) + labs(subtitle = "Silhouette")
print(p1)
print(p2)

# Exécution du K-Means 
k <- 2
# nstart=50 pour garantir le meilleur minimum global
set.seed(42)
res.kmeans <- kmeans(df_scaled, centers = k, nstart = 50)
df_sample$Cluster <- as.factor(res.kmeans$cluster)

# ==============================================================================
# ÉTAPE 5 : Analyse combinée
# ==============================================================================

fviz_cluster(res.kmeans, data = df_scaled, 
             geom = "point", ellipse.type = "norm", 
             ggtheme = theme_minimal(),
             main = "Clusters de Matchs (Les différents types de parties)")

# ==============================================================================
# ÉTAPE 6 : Interprétation (Lien avec la variable cible et Visualisations)
# ==============================================================================

# THE "WOW" FACTOR : Visualisation Ridge Plot (Densité)
# Montre comment l'avantage en Or (Gold Diff) se distribue pour chaque Cluster
ggplot(df_sample, aes(x = gold_diff, y = Cluster, fill = Cluster)) +
  geom_density_ridges(alpha = 0.7) +
  theme_ridges() + 
  labs(title = "Distribution du Différentiel d'Or par Type de Match (Cluster)",
       x = "Différentiel d'Or (Gold Diff)", y = "Cluster") +
  theme(legend.position = "none")

# Analyse métier décisive : Taux de victoire
df_sample$team_won_factor <- factor(df_sample$team_won, levels = c(0, 1), labels = c("Défaite", "Victoire"))

ggplot(df_sample, aes(x = Cluster, fill = team_won_factor)) +
  geom_bar(position = "fill") +
  theme_minimal() +
  labs(title = "Probabilité de Victoire selon la Dynamique du Match (Cluster)",
       x = "Type de Match (Cluster)", y = "Proportion",
       fill = "Résultat") +
  scale_fill_manual(values = c("#FC4E07", "#00AFBB"))
