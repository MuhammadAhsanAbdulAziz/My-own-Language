import ownLanguage

while True:
    text = input('My Language > ')
    result, error = ownLanguage.run(text)

    if error : print(error.as_string())
    else: print(result)