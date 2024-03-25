import random
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
import random
import string
from num2words import num2words
import datetime
from datetime import datetime, time, timedelta

def premiere_heure_jour():
    maintenant = datetime.now()
    premiere_heure = datetime.combine(maintenant.date(), time.min)
    return premiere_heure

def derniere_heure_jour():
    maintenant = datetime.now()
    derniere_heure = datetime.combine(maintenant.date(), time.max)
    return derniere_heure


def generer_code_couleur():
    # Génération de trois composantes de couleur en format hexadécimal
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    # Formatage des composantes en hexadécimal
    code_couleur = "#{:02x}{:02x}{:02x}".format(r, g, b)
    
    return code_couleur



def generate_strong_password(length=12):
    """Generate a strong password."""
    # Define character sets
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation

    # Combine character sets
    all_characters = lowercase_letters + uppercase_letters + digits + special_characters

    # Ensure at least one character from each set
    password = random.choice(lowercase_letters)
    password += random.choice(uppercase_letters)
    password += random.choice(digits)
    password += random.choice(special_characters)

    # Fill remaining length with random characters
    for _ in range(length - 4):
        password += random.choice(all_characters)

    # Shuffle the password to make it more random
    password_list = list(password)
    random.shuffle(password_list)
    password = ''.join(password_list)

    return password


def generate_code(prefix, position):
    date = datetime.now()
    f = str(date.year)[-2:] + f'{date.month:02d}' + f'{date.day:02d}' + f'{date.hour:02d}' + f'{date.minute:02d}' + f'{date.second:02d}'
    s = prefix + '{:08d}'.format(position) + f
    return s

def generate_random(prefix):
    s = prefix + '{:04d}'.format(random.randint(0, 9999))
    return s

def dechiffrement_cesar(message_chiffre, decalage):
        message_dechiffre = ""
        for caractere in message_chiffre:
            # Vérifier si le caractère est une lettre majuscule
            if caractere.isupper():
                ascii_code = ord(caractere)
                nouveau_code = (ascii_code - ord('A') - decalage) % 26 + ord('A')
                message_dechiffre += chr(nouveau_code)
            # Vérifier si le caractère est une lettre minuscule
            elif caractere.islower():
                ascii_code = ord(caractere)
                nouveau_code = (ascii_code - ord('a') - decalage) % 26 + ord('a')
                message_dechiffre += chr(nouveau_code)
            # Vérifier si le caractère est un chiffre
            elif caractere.isdigit():
                ascii_code = ord(caractere)
                nouveau_code = (ascii_code - ord('0') - decalage) % 10 + ord('0')
                message_dechiffre += chr(nouveau_code)
            # Si le caractère est un caractère spécial, le laisser inchangé
            else:
                message_dechiffre += caractere
        return message_dechiffre
    

def chiffrement_cesar(message, decalage) -> str:
    message_chiffre = ""
    for caractere in message:
        # Vérifier si le caractère est une lettre majuscule
        if caractere.isupper():
            ascii_code = ord(caractere)
            nouveau_code = (ascii_code - ord('A') + decalage) % 26 + ord('A')
            message_chiffre += chr(nouveau_code)
        # Vérifier si le caractère est une lettre minuscule
        elif caractere.islower():
            ascii_code = ord(caractere)
            nouveau_code = (ascii_code - ord('a') + decalage) % 26 + ord('a')
            message_chiffre += chr(nouveau_code)
        # Vérifier si le caractère est un chiffre
        elif caractere.isdigit():
            ascii_code = ord(caractere)
            nouveau_code = (ascii_code - ord('0') + decalage) % 10 + ord('0')
            message_chiffre += chr(nouveau_code)
        # Si le caractère est un caractère spécial, le laisser inchangé
        else:
            message_chiffre += caractere
    return message_chiffre

def sendMail(template, context, subject, mailFrom, mailTo):
    try:
        html_message = render_to_string(template,context=context)
        plain_message = strip_tags(html_message)
        message = EmailMultiAlternatives(subject=subject,
                                            from_email=mailFrom,
                                            to=[mailTo],
                                            body=plain_message,                      
        )
        message.attach_alternative(html_message, "text/html")
        message.send()
    except:
        return False
    return True

def nombre_en_lettres(nombre):
    # Conversion du nombre en mots en utilisant la langue française
    nombre_en_mots = num2words(nombre, lang='fr')
    
    return nombre_en_mots