[Open topic with navigation](../../../../../CANoeDEFamily.htm#Topics/CAPLFunctions/Security/Functions/CAPLfunctionSecurityLocalEncryptAES128ECB.md)

[CAPL Functions](../../CAPLfunctions.md) » [Security](../CAPLFunctionsSecurityOverview.md) » SecurityLocalEncryptAES128ECB

# SecurityLocalEncryptAES128ECB

[Valid for](../../../Shared/FeatureAvailability.md):  CANoe DE • CANoe4SW DE

**Note**  
Replaces `LocalSecurityEncryptAES128ECB`.

## Function Syntax

```
long SecurityLocalEncryptAES128ECB(byte key[], dword keyLength, byte data[], dword dataLength, byte cipheredData[], dword cipheredDataLength)
```

## Description

Encrypts data with a given key using AES128 (ECB), Padding Mode PKCS5.

## Parameters

- **byte key[]**  
  The key to be used for AES (128 bit).

- **dword keyLength**  
  16 (bytes).

- **byte data[]**  
  The data to encrypt.

- **dword dataLength**  
  The length of the data to encrypt.

- **byte cipheredData [] [Out]**  
  The buffer in which the ciphered data is stored.

- **dword cipheredData Length [In/Out]**  
  The length of the buffer. Typically this buffer has to be 16 bytes longer than the length of the data to encrypt.

## Return Values

- **1**  
  Success  
  A Value of 1 means that the action was successful.

- **<= 0**  
  Error  
  A value less than or equal to 0 means error.

## Example

```c
void Encrypt1(byte E1[])
{
  byte BaseKey[16] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
  byte Data[16] = {0x01,0x23,0x45,0x67,0x89,0xAB,0xCD,0xEF,0x01,0x23,0x45,0x67,0x89,0xAB,0xCD,0xEF};
  byte Result[32];
  dword length = elCount(Result);
  int i;
  dword res;

  res = SecurityLocalEncryptAES128ECB(BaseKey, elCount(BaseKey), Data, elCount(Data), Result, length);

  write("SecurityLocalEncryptAES128ECB Result: %d", res);
  for(i = 0; i < length; i++) write("Result Byte %d : %x", i, Result[i]);
}
```

© Vector Informatik GmbH  
CANoe (Desktop Editions & Test Bench Editions) Version 18 SP3  
[Contact/Copyright/License](../../../Shared/ContactCopyrightLicense.md)  
[Data Privacy Notice](https://www.vector.com/int/en/company/get-info/privacy-policy/)