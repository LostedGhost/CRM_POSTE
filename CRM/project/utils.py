import random


def generate_code(prefix, position):
    s = prefix + '{:05d}'.format(position)
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

