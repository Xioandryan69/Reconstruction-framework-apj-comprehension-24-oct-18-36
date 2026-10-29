# → crée sortie/ (ou sortie/<nom_racine> si la racine n'est pas ".")
#   avec tous les dossiers et fichiers vides

cd ~/Documents/GitHub/Reconstruction-framework-apj-comprehension-24-oct-18-36/script
python3 recreate.py structure.txt sortie


mkdir -p ../projet-standart-Copie
cp -av ./sortie/. ../projet-standart-Copie/

rm -rf sortie