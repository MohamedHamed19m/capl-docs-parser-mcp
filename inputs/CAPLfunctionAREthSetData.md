[Open topic with navigation](../../../../../../CANoeDEFamily.htm#Topics/CAPLFunctions/IP/AUTOSARethIL/Functions/CAPLfunctionAREthSetData.md)

**CAPL Functions** » **Ethernet** » **AUTOSAR Eth IL** » **AREthSetData**

# AREthSetData

[Valid for](../../../../Shared/FeatureAvailability.md): CANoe DE • CANoe4SW DE

## Function Syntax

- `long AREthSetData(dword messageHandle, dword dataLength, char data[]); // form 1`
- `long AREthSetData(dword messageHandle, dword dataLength, byte data[]); // form 2`
- `long AREthSetData(dword messageHandle, dword dataLength, struct data); // form 3`

## Description

This function can be used to set the payload of a SOME/IP message. If data in the payload of the message already exist, the data will be overwritten with this function call. If necessary the length field in the SOME/IP Message Header will be adapted at the function call.

## Parameters

- **messageHandle**: Handle of the received SOME/IP message (see [OnAREthMessage](CAPLfunctionOnAREthMessage.md))
- **dataLength**: Number of data bytes
- **data**: Data that should be copied to the SOME/IP message

## Return Values

- **0**: The function was successfully executed
- **>0**: [Error code](../CAPLfunctionsAREthILErrorCodes.md)

## Example

```plaintext
on key 's'
{
  dword messageId = 0x12340004; // service ID = 0x1234, method ID = 0x0004
  dword requestId = 0; // client ID = 0, session ID = 0
  dword protocolVersion = 1;
  dword interfaceVersion = 1;
  dword messageType = 0x2; // notification message
  dword returnCode = 0; // not available
  dword aep = 0; // application endpoint handle
  dword messageHandle = 0; // handle of the created SOME/IP message
  BYTE payload[5]; // the message payload
  dword count = 0; // a simple counter

  // initialize the payload
  count = 0;
  payload[count++] = 0x11;
  payload[count++] = 0x22;
  payload[count++] = 0x33;
  payload[count++] = 0x44;
  payload[count++] = 0x55;

  // open application endpoint
  aep = AREthOpenLocalApplicationEndpoint(17, 50002);

  // create the SOME/IP message itself and set the message payload
  messageHandle = AREthCreateMessage(messageId,requestId,protocolVersion,interfaceVersion,messageType,returnCode);
  AREthSetData(messageHandle,elcount(payload),payload);

  // send the SOME/IP message
  AREthOutputMessage(aep,0xFFFFFFFF,40001,messageHandle);

  // release the some IP message
  AREthReleaseMessage(messageHandle);
}
```

[See Also](javascript:void(0);)
```markdown
- [AREthGetData](CAPLfunctionAREthGetData.md#aanchor2564)
- [AREthIsOptional](CAPLfunctionAREthIsOptional.md#aanchor26055)
- [AREthSerializeMessage](CAPLfunctionAREthSerializeMessage.md#aanchor18598)
- [AREthSetData](#aanchor7749)
- [SomeIpIsOptional](../../SOMEIPIL/Functions/CAPLfunctionSomeIpIsOptional.md#aanchor16904)
```

© Vector Informatik GmbH

CANoe (Desktop Editions & Test Bench Editions) Version 18 SP3

[Contact/Copyright/License](../../../../Shared/ContactCopyrightLicense.md)

[Data Privacy Notice](https://www.vector.com/int/en/company/get-info/privacy-policy/)