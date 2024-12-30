import math

p = 491
q = 487
n = p * q
phi_n = (p - 1) * (q - 1)

e = 65537
while math.gcd(e, phi_n) != 1:
    e += 1

def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

d = mod_inverse(e, phi_n)


def rsa_decrypt(value):
    return pow(value, d, n)


def decrypt_log_file(log_file):
    decrypted_logs = []
    with open(log_file, "r") as file:
        for line in file:
            encrypted_values = line.strip().split()  # Get space-separated encrypted integers
            decrypted_line = "".join(chr(rsa_decrypt(int(value))) for value in encrypted_values)
            decrypted_logs.append(decrypted_line)
    return decrypted_logs


log_file = "exam_logs.txt"

# Decrypt log file and display results
decrypted_logs = decrypt_log_file(log_file)
print("Decrypted Logs:")
for log in decrypted_logs:
    print(log)
