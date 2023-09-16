import uks256


key = uks256.UKey.new()
cipher = uks256.Cipher(key=key)

plain = "Hello World!"

sal = cipher.encrypt(plain)
dec = cipher.decrypt(sal)

print(key)
print(sal)
print(dec)