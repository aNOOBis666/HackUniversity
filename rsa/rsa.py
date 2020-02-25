import random


def is_prime(n):
    """
       >>> is_prime(2)
       True
       >>> is_prime(11)
       True
       >>> is_prime(9)
       False
       """
    if n == 1:
        return False
    if n == 2:
        return True
    for x in range(3, n):
        if n % x == 0:
            return False
        else:
            return True
    return is_prime(n)


def gcd(a, b):
    """
    >>> gcd(12, 15)
    3
    >>> gcd(3, 7)
    1
    """
    while a != 0 and b != 0:
        if a > b:
            a = a % b
        else:
            b = b % a

    return a + b


def multiplicative_inverse(e: int, phi: int) -> int:
    """
        >>> multiplicative_inverse(7, 40)
        23
        """
    div = []
    rows = 0
    phi_temp = phi
    while phi_temp % e != 0:
        div.append(phi_temp // e)
        phi_temp, e = e, phi_temp % e
        rows += 1
    x = 0
    y = 1
    for i in range(rows -1, -1, -1):
        x, y = y, x - (y * div[i])
    return y % phi


def generate_keypair(p: int, q: int):

    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')

    n = p * q

    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    d = multiplicative_inverse(e, phi)

    return (e, n), (d, n)


def encrypt(pk, plaintext):
    key, n = pk
    cipher = [(ord(char) ** key) % n for char in plaintext]
    return cipher


def decrypt(pk, ciphertext):
    key, n = pk
    plain = [chr((char ** key) % n) for char in ciphertext]
    return ''.join(plain)


if __name__ == '__main__':
    print("RSA Encrypter/ Decrypter")
    p = int(input("Enter a prime number (17, 19, 23, etc): "))
    q = int(input("Enter another prime number (Not one you entered above): "))
    print("Generating your public/private keypairs now . . .")
    public, private = generate_keypair(p, q)
    print("Your public key is ", public, " and your private key is ", private)
    message = input("Enter a message to encrypt with your private key: ")
    encrypted_msg = encrypt(private, message)
    print("Your encrypted message is: ")
    print(''.join(map(lambda x: str(x), encrypted_msg)))
    print("Decrypting message with public key ", public, " . . .")
    print("Your message is:")
    print(decrypt(public, encrypted_msg))

