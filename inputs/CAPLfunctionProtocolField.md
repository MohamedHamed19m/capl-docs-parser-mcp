[Open topic with navigation](../../../../../CANoeDEFamily.htm#Topics/CAPLFunctions/IP/Selectors/CAPLfunctionProtocolField.md)

**CAPL Functions** » [Ethernet](../CAPLEthernetStartPage.md) » [Function Overview](../CAPLfunctionsIPOverview.md) » [ethernetPacket](../Objects/CAPLfunctionEthernetPacket.md) » Selector `<protocol>.<field>`

# ethernetPacket Selectors: `<protocol>.<field>`

[Valid for](../../../Shared/FeatureAvailability.md):  CANoe DE • CANoe4SW DE

## Selectors

- `byte ethernetPacket.<protocol>.<field>;`
- `word ethernetPacket.<protocol>.<field>;`
- `dword ethernetPacket.<protocol>.<field>;`
- `qword ethernetPacket.<protocol>.<field>;`

## Description

Read or write access to protocol fields. See protocol overview for protocol and field designators. If `<protocol>` or `<field>` is not contained in the packet, the measurement is stopped with a runtime error. `ethernetPacket::<protocol>::IsAvailable` and `ethernetPacket::<protocol>::<field>::IsAvailable` can be used to find out if the field is available.

The data type depends on the protocol field. The bit length is rounded up to next larger CAPL data type, i.e. a 4-bit protocol field will use byte and a 12 bit protocol field will use word.

This selector is available for protocol field of type integer. For protocol fields, which are not of type integer, the method `GetData` and `SetData` can be used.

## Parameters

—

## Return Values

Value of the protocol field.

## Example

```plaintext
ethernetPacket pkt;

// initialize packet with IPv4 and UDP protocols
pkt.udp.Init();

// set IPv4 addresses
pkt.ipv4.source.ParseAddress("192.168.1.1");
pkt.ipv4.destination.ParseAddress("192.168.1.255");

// set UDP ports
pkt.udp.source = 40001;
pkt.udp.destination = 40002;

// set UDP payload
pkt.udp.SetData(0, "Hello", 5);

// calculate UDP and IPv4 checksum and send Ethernet packet
pkt.CompletePacket();
output(pkt);
```

© Vector Informatik GmbH

CANoe (Desktop Editions & Test Bench Editions) Version 18 SP3

[Contact/Copyright/License](../../../Shared/ContactCopyrightLicense.md) | [Data Privacy Notice](https://www.vector.com/int/en/company/get-info/privacy-policy/)