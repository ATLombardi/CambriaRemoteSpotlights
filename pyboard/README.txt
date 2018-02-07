key = USB_VID val = f055
key = USB_PID_CDC_MSC val = 9800
key = USB_PID_CDC_HID val = 9801
key = USB_PID_CDC val = 9802
; Windows USB CDC ACM Setup File
; Based on INF files which were:
;     Copyright (c) 2000 Microsoft Corporation
;     Copyright (C) 2007 Microchip Technology Inc.
; Likely to be covered by the MLPL as found at:
;    <http://msdn.microsoft.com/en-us/cc300389.aspx#MLPL>.

[Version]
Signature="$Windows NT$"
Class=Ports
ClassGuid={4D36E978-E325-11CE-BFC1-08002BE10318}
Provider=%MFGNAME%
Layou