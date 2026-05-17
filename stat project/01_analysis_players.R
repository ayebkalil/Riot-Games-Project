# ==============================================================================
# Mini-Projet : Analyse Multivariée - Profilage des Joueurs (Rank Features)
# ==============================================================================

# 1. Chargement des packages nécessaires
# Décommentez la ligne ci-dessous si des packages manquent :
# install.packages(c("tidyverse", "FactoMineR", "factoextra", "cluster", "corrplot", "fmsb"))
library(tidyverse)
library(FactoMineR)
library(factoextra)
library(cluster)
library(corrplot)
library(fmsb) # Pour les graphiques Radar (Spider plots)

# ==============================================================================
# ÉTAPE 1 & 2 : Compréhension et Préparation des données "Smart"
# ==============================================================================

# Chemin vers le dataset
file_path <- "C:/Users/ayebk/OneDrive/Desktop/hezou/Riot Games Project/data/processed/rank_features_enriched_v2.csv"
df_players <- read_csv(file_path)

# DÉCISION SMART 1 : Retrait des Outliers (Valeurs aberrantes)
# Le K-means est très sensible aux outliers. Nous utilisons la méthode de 
# l'écart interquartile (IQR) pour nettoyer les valeurs extrêmes sur des stats clés.
remove_outliers <- function(df, col) {
  Q1 <- quantile(df[[col]], 0.25, na.rm = TRUE)
  Q3 <- quantile(df[[col]], 0.75, na.rm = TRUE)
  IQR <- Q3 - Q1
  lower_bound <- Q1 - 1.5 * IQR
  upper_bound <- Q3 + 1.5 * IQR
  df %>% filter(!!sym(col) >= lower_bound & !!sym(col) <= upper_bound)
}

# Nettoyage des NA puis retrait des outliers sur le KDA et les dégâts
df_clean <- drop_na(df_players) %>%
  remove_outliers("avg_kda") %>%
  remove_outliers("avg_damage_per_min")
library(dplyr)

df_quant <- df_clean %>%
  dplyr::select(
    avg_kda,
    avg_cs_per_min,
    avg_gold_per_min,
    avg_damage_per_min,
    avg_vision_per_min,
    win_rate,
    soloKills,
    turretPlates
  )

# DÉCISION SMART 2 : Analyse de colinéarité
# On vérifie si certaines variables portent la même information.
cor_matrix <- cor(df_quant)
corrplot(cor_matrix, method = "circle", type = "upper", 
         tl.col = "black", tl.srt = 45,
         title = "Matrice de corrélation (Identifier la colinéarité)",
         mar = c(0,0,2,0))

# ==============================================================================
# ÉTAPE 3 : Analyse Factorielle (ACP) Améliorée
# ==============================================================================

# L'ACP permet justement de contourner la colinéarité en créant des axes indépendants.
res.pca <- PCA(df_quant, scale.unit = TRUE, ncp = 5, graph = FALSE)

# Variance expliquée
fviz_eig(res.pca, addlabels = TRUE, ylim = c(0, 50), 
         main = "Graphique des éboulis (Scree plot)")

# DÉCISION SMART 3 : Filtrer le cercle des corrélations par Cos2 (Qualité de représentation)
# On n'affiche que les variables bien représentées sur ces deux axes.
fviz_pca_var(
  res.pca,
  col.var = "cos2",
  gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
  repel = TRUE,
  select.var = list(cos2 = 0.5),
  title = "Cercle des corrélations (Variables bien représentées)"
)
# BIPLOT : Permet de voir simultanément les individus et les variables
fviz_pca_biplot(
  res.pca,
  geom.ind = "point",
  fill.ind = "gray",
  col.ind = "black",
  alpha.ind = 0.3,
  col.var = "red",
  repel = TRUE,
  title = "Biplot : Individus et Variables"
)

# ==============================================================================
# ÉTAPE 4 : Classification (K-Means) Robuste
# ==============================================================================

df_scaled <- scale(df_quant)

# DÉCISION SMART 4 : Validation du "k" via le score de Silhouette
# Utiliser deux méthodes montre une grande rigueur statistique.
p1 <- fviz_nbclust(df_scaled, kmeans, method = "wss") + labs(subtitle = "Méthode du coude")
p2 <- fviz_nbclust(df_scaled, kmeans, method = "silhouette") + labs(subtitle = "Score de Silhouette")
# Afficher les deux graphiques
print(p1)
print(p2)

# Choix de K selon les graphiques (Exemple: k = 3 ou 4)
k <- 3
# DÉCISION SMART 5 : nstart = 50
# Force l'algorithme à tester 50 points de départ initiaux pour éviter les minima locaux.
set.seed(123)
res.kmeans <- kmeans(df_scaled, centers = k, nstart = 50)
df_clean$Cluster <- as.factor(res.kmeans$cluster)

# ==============================================================================
# ÉTAPE 5 & 6 : Analyse combinée et Radar Charts (Spider Plots)
# ==============================================================================

fviz_cluster(res.kmeans, data = df_scaled, geom = "point", 
             ellipse.type = "convex", ggtheme = theme_minimal(),
             main = paste("Clusters K-Means (k =", k, ") projetés sur l'ACP"))

# ------------------------------------------------------------------------------
# THE "WOW" FACTOR : Les Radar Charts pour les profils
# ------------------------------------------------------------------------------

# Préparation des données pour le radar chart
cluster_profiles <- df_clean %>%
  group_by(Cluster) %>%
  summarise(
    across(
      c(
        avg_kda,
        avg_cs_per_min,
        avg_damage_per_min,
        avg_vision_per_min,
        win_rate
      ),
      mean
    )
  ) %>%
  dplyr::select(-Cluster) # On garde juste les valeurs

# On trouve les max et min pour définir l'échelle du radar
max_vals <- apply(cluster_profiles, 2, max) * 1.1
min_vals <- apply(cluster_profiles, 2, min) * 0.9
radar_data <- rbind(max_vals, min_vals, cluster_profiles)

# Tracé d'un graphique Radar superposant les clusters
colors_border <- c("#00AFBB", "#E7B800", "#FC4E07", "#228B22")
colors_in <- scales::alpha(colors_border, 0.2)

radarchart(radar_data, axistype=1, 
           pcol=colors_border, pfcol=colors_in, plwd=2, plty=1,
           cglcol="grey", cglty=1, axislabcol="grey", caxislabels=seq(0,20,5), cglwd=0.8,
           vlcex=0.8, title="Profil Moyen des Clusters (Radar Chart)")
legend(x="bottom", legend = paste("Cluster", 1:k), bty = "n", pch=20, col=colors_border, pt.cex=2, horiz = TRUE)
