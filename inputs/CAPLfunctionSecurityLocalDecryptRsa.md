[Open topic with navigation](../../../../../CANoeDEFamily.htm#Topics/CAPLFunctions/Security/Functions/CAPLfunctionSecurityLocalDecryptRsa.md)

**CAPL Functions** » [Security](../CAPLFunctionsSecurityOverview.md) » SecurityLocalDecryptRsa

# SecurityLocalDecryptRsa

[Valid for](../../../Shared/FeatureAvailability.md): CANoe DE • CANoe4SW DE

## Function Syntax

`SecurityLocalDecryptRsa(byte privateKey[], dword privateKeyLength, byte cipherData[], dword cipherDataLength, byte plainData[], dword* plainDataLength, dword paddingMode)`

## Description

Decrypts data with a given private key using asymmetric RSA encryption. Padding mode can be selected via the parameter.

## Parameters

- **privateKey**: The private key to be used for decryption in PKCS#8 format (with VSM 3.4.4 also PKCS#1 format is supported)
- **privateKeyLength**: Length of the private key to be used for decryption
- **cipherData**: Data to be decrypted
- **cipherDataLength**: Length of the data to be decrypted
- **plainData [OUT]**: Buffer to store decrypted data
- **plainDataLength [IN/OUT]**: Length of buffer to store decrypted data.
- **paddingMode**:
  - OAEP(SHA-256) = 1
  - OAEP(SHA-384) = 2
  - OAEP(SHA-512) = 3
  - PKCS1_v1_5 = 10
  - OAEP(SHA-1) = 12

## Return Values

- **1**: Success. A value of 1 means that the action was successful.
- **≤ 0**: Error. A value less than or equal to 0 means error.

## Example