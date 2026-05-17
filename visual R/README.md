# Visual R Results Summary

This file captures the results shown in the plots inside this folder.
No interpretation was added to the project report files.

## Files Covered

- Rplot.png
- Rplot01.png
- Rplot02.png
- Rplot03.png
- Rplot04.png
- Rplot05.png
- Rplot06.png
- Rplot07.png
- Rplot08.png
- Rplot09.png
- Rplot10.png
- Rplot11.png
- Rplot12.png
- Rplot13.png
- Rplot14.png
- Rplot15.png
- Rplot16.png
- Rplot17.png
- Rplot18.png

## Results By Figure

1. Rplot.png
   - Full 10-rank projection in PCA space shows strong overlap across rank groups.
   - Clear rank frontiers are not visible with the current feature space.

2. Rplot01.png
   - Grouping ranks into 3 ELO groups produces cleaner structure than 10 separate ranks.
   - Overlap remains but cluster boundaries are more usable.

3. Rplot02.png
   - CS/min distributions differ by merged ELO groups.
   - Group-wise density separation is improved after grouping High + Elite.

4. Rplot03.png
   - Correlation matrix highlights strong positive relations between key performance metrics.
   - Some variables show inverse relations, indicating potential multicollinearity patterns.

5. Rplot04.png
   - Scree plot: explained variance is front-loaded in first components.
   - First two dimensions carry a large share of information.

6. Rplot05.png
   - Correlation circle: Dim1 is aligned with economy/output style variables.
   - Dim2 adds secondary behavior signal (vision/KDA/win rate related structure).

7. Rplot06.png
   - PCA biplot of individuals + variables confirms a mostly continuous population spread.
   - No naturally perfect hard separation between all skill levels.

8. Rplot07.png
   - Elbow method suggests diminishing WSS gains after a low number of clusters.
   - Candidate range appears around k=2 to k=4.

9. Rplot08.png
   - Silhouette score peaks at k=2.
   - k=2 is the strongest compact/separated partition in this setting.

10. Rplot09.png
    - k=3 PCA cluster projection is visually interpretable.
    - Some overlap persists between neighboring clusters.

11. Rplot10.png
    - Radar chart shows distinct average profiles by cluster across selected metrics.
    - Clusters express different playstyle/performance signatures.

12. Rplot11.png
    - Match differential features are strongly related (gold, kills, objectives).
    - Death-related direction appears opposed to advantage-related variables.

13. Rplot12.png
    - Scree plot for match-dynamics PCA: first axis dominates (~68.4%).
    - Most variance is explained by one principal match-state direction.

14. Rplot13.png
    - Match-dynamics biplot: Dim1 corresponds to overall advantage/snowball direction.
    - Positive differentials align on one side, opposite side aligns with deaths.

15. Rplot14.png
    - Elbow analysis for match clustering favors low k.
    - Largest gain is from k=1 to k=2.

16. Rplot15.png
    - Silhouette for match clustering peaks at k=2.
    - k=2 is the preferred solution for this feature set.

17. Rplot16.png
    - Two match clusters separate clearly along dominant PCA axis.
    - Visual separation is stronger than in multi-rank player clustering.

18. Rplot17.png
    - Gold differential distributions are split: one negative-centered cluster, one positive-centered cluster.
    - This supports two opposite match-state regimes.

19. Rplot18.png
    - Win/loss proportions by cluster are highly polarized.
    - One cluster is mostly losses, the other mostly wins.

## Consolidated Outcome

- Rank-level modeling:
  - 10-rank separation is weak in this space.
  - 3 broad ELO groups are more tractable.

- Match-dynamics modeling:
  - A dominant first PCA axis captures most variance.
  - Two clusters (k=2) are consistently supported by elbow + silhouette + visual checks.
  - These two clusters align strongly with opposite game outcomes.
