import ownLanguage

while True:
    text = input('My Language > ')
    result, error = ownLanguage.run('<stdin>',text)

    if error : print(error.as_string())
    else: print(result)