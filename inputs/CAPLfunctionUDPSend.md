[Open topic with navigation](../../../../../CANoeDEFamily.htm#Topics/CAPLFunctions/TCPIPAPI/Functions/CAPLfunctionUDPSend.md)

# UdpSend

[CAPL Functions](../../CAPLfunctions.md) » [TCP/IP API](../CAPLfunctionsTCPIPOverview.md) » UdpSend

**Valid for**: CANoe DE • CANoe4SW DE

## Function Syntax

- `long UdpSend( dword socket, char buffer[], dword size); // form 1`
- `long UdpSend( dword socket, struct data, dword size); // form 2`
- `long UdpSend( dword socket, byte buffer[], dword size); // form 3`

## Method Syntax

- `long socket.Send(char buffer[], dword size); // form 1`
- `long socket.Send(struct data, dword size); // form 2`
- `long socket.Send(byte buffer[], dword size); // form 3`

## Description

The function sends data on a connected UDP socket. It is necessary to connect the socket with [UdpConnect](CAPLfunctionUDPConnect.md) before calling this function.

## Parameters

- **socket**: The socket handle.
- **buffer**: The buffer containing the data to be sent.
- **data**: The struct containing the data to be sent.
- **size**: The size of the data to be sent.

## Return Values

- **0**: The function completed successfully.
- **WSA_INVALID_PARAMETER (87)**: The specified socket was invalid.
- **SOCKET_ERROR (-1)**: The function failed. Call [IpGetLastSocketError](CAPLfunctionIPGetLastSocketError.md) to get a more specific error code.

## Example

```plaintext
variables
{
  UdpSocket gSocket;
}

on start
{
  gSocket = UdpSocket::Open( IP_Endpoint(0.0.0.0:0) );
  gSocket.Connect(ip_Endpoint(192.168.1.3:40002));
  gSocket.Send( "Request", 7 );
}
```

© Vector Informatik GmbH

CANoe (Desktop Editions & Test Bench Editions) Version 18 SP3

[Contact/Copyright/License](../../../Shared/ContactCopyrightLicense.md) | [Data Privacy Notice](https://www.vector.com/int/en/company/get-info/privacy-policy/)