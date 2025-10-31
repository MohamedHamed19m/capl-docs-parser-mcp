[Open topic with navigation](../../../../../CANoeDEFamily.htm#Topics/CAPLFunctions/IP/Methods/CAPLfunctionGetInt.md)

[CAPL Functions](../../CAPLfunctions.md) » [Ethernet](../CAPLEthernetStartPage.md) » [Function Overview](../CAPLfunctionsIPOverview.md) » ethernetPacket::GetInt

# ethernetPacket::GetInt

[Valid for](../../../Shared/FeatureAvailability.md): CANoe DE • CANoe4SW DE

## Method Syntax

[int ethernetPacket.GetInt(char protocol[], char field[])](../Objects/CAPLfunctionEthernetPacket.htm)

## Description

Returns the value of the specified field as **int**.

If **protocol** or **field** is not contained in the packet, the measurement is stopped with a runtime error. [ethernetPacket::IsAvailable](CAPLfunctionIsAvailable.md) can be used to find out if the field is available.

## Parameters

- **protocol**: Name of the [protocol](../../../CANoeCANalyzer/Ethernet/Protocols/Protocol.md).
- **field**: Name of the field.

## Return Values

Value of the field.

## Example

```plaintext
on ethernetPacket *
{
  if(this.IsAvailable("icmpv4", "echo.identifier"))
  {
    Write("icmpv4.echo.identifier has value %d", this.GetInt("icmpv4", "echo.identifier"));
  }
}
```

© Vector Informatik GmbH

CANoe (Desktop Editions & Test Bench Editions) Version 18 SP3

[Contact/Copyright/License](../../../Shared/ContactCopyrightLicense.md) | [Data Privacy Notice](https://www.vector.com/int/en/company/get-info/privacy-policy/)