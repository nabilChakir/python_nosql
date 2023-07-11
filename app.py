from flask import Flask, render_template, request, render_template_string, redirect, url_for
from markupsafe import escape   

# Pymongo est une bibliothèque Python qui permet d'interagir avec MongoDB, un système de gestion de bases 
# de données NoSQL orienté document.
import pymongo
import datetime
import re

## NoSQL
# Connexion à MongoDB
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# Création de la DB "flaskDB" si elle n'existe pas et établissement d'une connexion avec celle-ci.
# Remarque importante: Dans MongoDB, une DB n'est pas créée tant qu'elle n'a pas de contenu, 
# donc pour réellement la créer, il faut créer une collection et au moins un document dans cette collection
mydb = myclient["flaskDB"]

print(myclient.list_database_names())   # checkpoint

# Création de la collection "formulaire" si elle n'existe pas, contenue dans la DB "flaskDB"
mycol = mydb["formulaire"]

print(mydb.list_collection_names())     # checkpoint

def updateDB(nom, prenom, genre, pays, email, sujets, message):
    if "formulaire" in mydb.list_collection_names():
        # last_doc est un objet itérable de type Cursor retourné par la méthode find() de PyMongo. 
        # Un curseur dans PyMongo est un objet itérable qui représente un ensemble de résultats de requête 
        # dans MongoDB. Il vous permet de parcourir les documents individuels dans le résultat de la requête.
        last_doc = mycol.find({}, {"_id": 1}).sort("_id", -1)
        # L'indice 0 représente l'indice du document JSON  de la requête mycol.find(match_argument,projection_argument)
        # et "_id" représente la clé de la valeur de l'id de ce document.
        id = last_doc[0]["_id"] + 1
    else:
        id = 1
   
    print(id)   # checkpoint

    mydoc = { "_id": id, 
            "dateHeure": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            "identifiants": {"nom": nom, "prenom": prenom,  "genre": genre, "pays": pays, "email": email},
            "sujets": sujets,
            "message": message}

    # La méthode insert_one() renvoie un objet InsertOneResult, qui a une propriété, insert_id, qui contient 
    # l'identifiant du document inséré.
    x=mycol.insert_one(mydoc)
    print(x.inserted_id) # checkpoint
    
    print("DB updated!!")
##

app = Flask(__name__)

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/traitement', methods=['POST','GET'])
def submit_form():

    if request.method == 'POST':
        # SANITISATION des entrées utilisateur
        prenom = escape(request.form.get('prenom'))
        nom = escape(request.form.get('nom'))
        email = escape(request.form.get('email'))
        message = escape(request.form.get('message'))
        pays = escape(request.form.get('pays'))
        genre = escape(request.form.get('genre'))
        sujets = request.form.getlist('sujets')

        honeypot = request.form.get('spam')
        # Si le champ honeypot est rempli, c'est probablement une soumission de spam
        if honeypot:
            return render_template_string('Salut le bot!') 

        # VALIDATION des entrées utilisateur
        errors = []  # Liste pour stocker les messages d'erreur
        prenom_pattern = r"^[A-Za-z]{3,15}$"
        email_pattern = r"^[\w.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(prenom_pattern, prenom):
           errors.append("Le prénom n'est pas valide.")

        if not re.match(prenom_pattern, nom):
            errors.append("Le nom n'est pas valide.")

        if not re.match(email_pattern, email):
            errors.append("Le mail n'est pas valide.")
        else:
            if ".." in email:
                errors.append("Le mail n'est pas valide.")

        if not pays:
            errors.append("Veuillez sélectionner un pays!")

        # if not genre: pq cette condition ne fonctionne pas correctement selon chatGPT
        # Dans le cas des radio buttons, si aucun bouton n'est sélectionné, aucun champ avec le même nom ne 
        # sera envoyé dans request.form. Cela signifie que la clé 'genre' ne sera pas présente dans request.form 
        # du tout, et non pas avec une valeur vide ("").

        # Par conséquent, dans votre code initial, la condition if not genre ne sera pas satisfaite lorsque 
        # vous soumettez le formulaire sans sélectionner de genre, car genre n'est pas dans request.form du tout.
        # if 'genre' not in request.form:
        # if not genre: ne fonctionne que si le genre n'est pas echappé!!!!!!! 
        if genre not in ['H','F']:
            errors.append("Veuillez sélectionner un genre")
        
        if not message:
            errors.append("Veuillez entrer un message")
        
        if not sujets:
            sujets.append('Autre')
        
        if errors:
            return render_template('index.html', errors=errors)
    
        updateDB(nom, prenom, genre, pays, email, sujets, message)
        
        return render_template('thankyou.html', prenom=prenom, nom=nom, email=email, pays=pays, message=message, genre=genre, sujets=sujets)
    
    else:
        return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.config['DEBUG'] = False  # à ne jamais mettre en True en PRODUCTION (fait pour aider le DEVELOPPEMENT)
    app.run()


    





