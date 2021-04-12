from cryptography.fernet import Fernet
from pathlib import Path

eKey = "Ln0QvS5tpSM2-yibcwDXbqmxcKd2GxoY5d5da-DIGG0="
path = str(Path.cwd()) + "/keylogs/"
filename = input("Enter name of file to decrypt: ")
file = Path(path + filename + '.txt')

if file.is_file():
    with open(file, 'rb') as f:
        data = f.read()
    fernet = Fernet(eKey)
    decrypted = fernet.decrypt(data)
    with open(Path(path + filename + '_decrypted.txt'), 'wb') as f:
        f.write(decrypted)
    print("File has been decrypted")
else:
    print("File does not exist")

