import os,math,codecs,zlib,base64,random

class UKey:
    def new()->str:
        pure = os.urandom(256).hex()
        chunks = []
        salt = random.choice(UKey.__prime_gen__(M=90000))

        for i in range(0, len(pure), 32):
            chunk = pure[i:i + 32]
            chunks.append(chunk)
        signature = "          #UKS256-Sign\n"+("="*32)+f"\n            <{salt}>\n"+'\n'.join(chunks)+"\n"+("="*32)
        return signature
    
    def __prime_gen__(M:int)->list[int]:
        result=[2,3]; a=5; b=7; count=3; factor=[5]; threshold=25    
        while a<M:      
            if a==threshold:
                factor.append(result[count])
                threshold=factor[-1]**2
                count+=1
            elif all(a%k for k in factor): result.append(a)
            if b>=M: break
            elif b==threshold:
                factor.append(result[count])
                threshold=factor[-1]**2
                count+=1
            elif all(b%k for k in factor): result.append(b)
            a+=6; b+=6
        return result
    
    def retrieve(signature:str)->(int, bytearray):
        pure = signature.splitlines()
        del pure[0]; del pure[0]; pure.pop()
        salt=int(pure[0].strip()[1:][:-1])
        return (salt, bytearray.fromhex(''.join(pure[1:])))

class Cipher():
    def __init__(self, key:str):
        self.iv, self.key=UKey.retrieve(key)

    def __key_calc__(self):
        keylog = 0
        for byte in self.key:
            x= ((((byte * (32+len(str(self.iv)))) >> 8) // 2)+2 ** 2)
            keylog+=x
        return keylog
    
    def encrypt(self, plain:str)->str:
        cipharray = ""
        keylog = self.__key_calc__()
        for byte in bytearray(plain.encode('utf-8')):
            cipharray+=chr(
                ((byte**2)^keylog)<<2
            )
        comp=zlib.compress(cipharray.encode(), zlib.Z_BEST_COMPRESSION).hex()
        return base64.b32encode(codecs.encode(codecs.encode(comp, "punycode"), "quopri_codec")).decode()

    def decrypt(self, ciphstr:str)->str:
        ciphstr=zlib.decompress(bytes.fromhex(codecs.decode(codecs.decode(base64.b32decode(ciphstr), "quopri_codec"), "punycode"))).decode()
        plain = ""
        keylog = self.__key_calc__()
        for byte in ciphstr:
            plain+=chr(
                int(math.sqrt((ord(byte)>>2)^keylog))
            )
        return plain