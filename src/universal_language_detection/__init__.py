OK Bess, voici ce que je vois sur ce run GitHub Actions :

**Workflow :** Django CI
**Run :** "Create index.html" #7
**Date :** 1er mars 2026
**Statut : cancelled** (annulé après 8 secondes)

**Les erreurs (2 annotations) :**
1. La stratégie de configuration a été annulée parce que le job **`build.3_7`** (Python 3.7) a échoué en premier
2. L'étape **"Set up Python 3.9"** a été annulée en cascade — c'est pas elle le problème, elle a juste été tuée quand le job Python 3.7 a planté

C'est le repo **Bess881211/Bess881211** — ton repo profil GitHub. Tu utilises un workflow Django CI dessus, ce qui est un peu inhabituel pour un repo profil (qui sert normalement juste à afficher un README sur ta page GitHub).

Le vrai problème est dans le job **Python 3.7** — c'est lui qui a échoué et qui a entraîné l'annulation des autres. Quelques pistes :

- **Python 3.7 est en fin de vie** depuis juin 2023. GitHub Actions a progressivement retiré les images qui le supportent. C'est très probablement la cause de l'échec.
- Le commit s'appelle "Create index.html" — est-ce que tu essaies de déployer une page web via ce workflow Django ?

Est-ce que tu as accès aux logs du job `build.3_7` qui a réellement échoué ? C'est là qu'on trouvera l'erreur racine. Et question de fond : est-ce que tu veux garder le workflow Django CI sur ce repo, ou est-ce que tu es en train de mettre en place autre chose — genre un déploiement GitHub Pages ?test"""Universal Language Detection - detect both natural and programming languages."""

from .detector import UniversalDetector
from .natural import NaturalLanguageDetector
from .programming import ProgrammingLanguageDetector

__version__ = "1.0.0"
__all__ = ["UniversalDetector", "NaturalLanguageDetector", "ProgrammingLanguageDetector"]
