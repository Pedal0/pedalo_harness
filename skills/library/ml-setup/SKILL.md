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

## Étape 2 — Choisir l'installation PyTorch

| Hardware détecté | Commande |
|---|---|
| Pas de GPU NVIDIA | `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| GPU compute capability 12.x (RTX 50xx / Blackwell) | `pip install torch --index-url https://download.pytorch.org/whl/cu128` |
| GPU compute capability 8.x / 9.x (RTX 30xx/40xx) | `pip install torch --index-url https://download.pytorch.org/whl/cu124` |

Ne jamais faire `pip install torch` sans index : la build par défaut peut
être incompatible avec le GPU détecté.

Vérifier après installation :
`python -c "import torch; print(torch.cuda.is_available())"`

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