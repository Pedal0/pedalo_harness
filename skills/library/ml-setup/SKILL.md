---
name: ml-setup
description: Détecter le hardware disponible et installer le bon environnement ML (PyTorch CPU ou CUDA, AutoGluon, FLAML). À utiliser dès que l'utilisateur veut entraîner un modèle, faire du machine learning, du deep learning ou de l'AutoML, avant toute écriture de script d'entraînement.
---

# ML environment setup

## RÈGLE ABSOLUE

Ne JAMAIS installer un paquet ML avant d'avoir exécuté l'étape 1.
Le hardware détermine la commande d'installation. Une mauvaise commande
installe une build inutilisable (CPU sur machine GPU, ou kernels
incompatibles).

## Étape 1 — Détecter le hardware

Écris ce script dans `detect_hw.py` avec write_file, puis exécute-le avec bash :

```python
import platform, shutil, subprocess, os

print(f"OS: {platform.system()} {platform.machine()}")
print(f"CPU cores: {os.cpu_count()}")

try:
    import psutil
    print(f"RAM GB: {psutil.virtual_memory().total / 1e9:.0f}")
except ImportError:
    print("RAM GB: unknown (psutil not installed)")

if shutil.which("nvidia-smi"):
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
         "--format=csv,noheader"],
        capture_output=True, text=True
    )
    print(f"GPU: {out.stdout.strip()}")
else:
    print("GPU: none")

try:
    import torch
    print(f"torch: {torch.__version__}, cuda_available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"compute capability: {torch.cuda.get_device_capability(0)}")
except ImportError:
    print("torch: not installed")
```

## Étape 2 — Installation de PyTorch : rediriger l'utilisateur

Les commandes d'installation PyTorch dépendent de la version CUDA et changent
régulièrement. N'invente JAMAIS une commande pip pour torch, et n'exécute pas
d'installation toi-même.

À la place :
1. Rapporte le hardware détecté à l'étape 1 (GPU, compute capability, driver).
2. Dirige l'utilisateur vers le sélecteur officiel : https://pytorch.org/get-started/locally/
   Il y choisit son OS, son gestionnaire de paquets et sa version CUDA,
   et le site génère la commande exacte à jour.
3. Attends que l'utilisateur confirme l'installation faite.
4. Vérifie ensuite avec bash :
   `python -c "import torch; print(torch.__version__, torch.cuda.is_available())"`
   - Si `cuda_available` est False alors qu'un GPU a été détecté à l'étape 1 :
     signale-le, c'est probablement une build CPU installée par erreur.
   - Si torch n'est pas installé, redemande à l'utilisateur.

Si aucun GPU n'a été détecté, la version CPU par défaut convient et
l'utilisateur peut installer sans se soucier de l'index CUDA.

## Étape 3 — Choisir la librairie AutoML

| Situation | Librairie | Pourquoi |
|---|---|---|
| Dataset < 10k lignes, ou budget < 10 min, ou CPU seul modeste | FLAML | léger, rapide, installation triviale |
| Dataset tabulaire sérieux, recherche de performance | AutoGluon | ensembling multi-couches, meilleurs benchmarks |
| Images / texte / multimodal | AutoGluon (MultiModal) | seul des deux à les couvrir |
| Architecture custom, besoin de contrôle total | PyTorch direct | pas d'AutoML |

Installation :
- FLAML : `pip install "flaml[automl]"`
- AutoGluon : `pip install autogluon.tabular[all]` (long : plusieurs minutes)

## Étape 4 — Rapporter à l'utilisateur

Avant d'installer quoi que ce soit, annonce :
- le hardware détecté,
- la librairie choisie et pourquoi,
- la commande d'installation exacte,
- le temps d'installation estimé.

Puis demande confirmation.