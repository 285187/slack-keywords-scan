from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os, stat
buffer_size = 65536  
key_slack_scan_file = 'key.key'

input_file = open('results.csv' , 'rb')
output_file = open('results_decrypted.csv' , 'wb')
key_file = open(key_slack_scan_file, 'rb')
iv = input_file.read(16)
ik = key_file.read(32)
cipher_encrypt = AES.new(ik, AES.MODE_CFB, iv=iv)
buffer = input_file.read(buffer_size)
while len(buffer) > 0:
    decrypted_bytes = cipher_encrypt.decrypt(buffer)
    output_file.write(decrypted_bytes)
    buffer = input_file.read(buffer_size)
input_file.close()
output_file.close()
os.chmod('results_decrypted.csv', stat.S_IRWXU)