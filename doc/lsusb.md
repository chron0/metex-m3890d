```
 Bus 009 Device 116: ID 0925:1234 Lakeview Research
 Device Descriptor:
   bLength                18
   bDescriptorType         1
   bcdUSB               1.10
   bDeviceClass            0
   bDeviceSubClass         0
   bDeviceProtocol         0
   bMaxPacketSize0         8
   idVendor           0x0925 Lakeview Research
   idProduct          0x1234
   bcdDevice            1.00
   iManufacturer           1 USB DMM
   iProduct                2 USB DMM
   iSerial                 0
   bNumConfigurations      1
   Configuration Descriptor:
     bLength                 9
     bDescriptorType         2
     wTotalLength           34
     bNumInterfaces          1
     bConfigurationValue     1
     iConfiguration          0
     bmAttributes         0x80
       (Bus Powered)
     MaxPower              100mA
     Interface Descriptor:
       bLength                 9
       bDescriptorType         4
       bInterfaceNumber        0
       bAlternateSetting       0
       bNumEndpoints           1
       bInterfaceClass         3 Human Interface Device
       bInterfaceSubClass      0
       bInterfaceProtocol      0
       iInterface              0
         HID Device Descriptor:
           bLength                 9
           bDescriptorType        33
           bcdHID               1.10
           bCountryCode            0 Not supported
           bNumDescriptors         1
           bDescriptorType        34 Report
           wDescriptorLength      52
           Report Descriptor: (length is 52)
             Item(Global): Usage Page, data= [ 0xa0 0xff ] 65440
                             (null)
             Item(Local ): Usage, data= [ 0x01 ] 1
                             (null)
             Item(Main  ): Collection, data= [ 0x01 ] 1
                             Application
             Item(Local ): Usage, data= [ 0x02 ] 2
                             (null)
             Item(Main  ): Collection, data= [ 0x00 ] 0
                             Physical
             Item(Global): Usage Page, data= [ 0xa1 0xff ] 65441
                             (null)
             Item(Local ): Usage, data= [ 0x03 ] 3
                             (null)
             Item(Local ): Usage, data= [ 0x04 ] 4
                             (null)
             Item(Global): Logical Minimum, data= [ 0x80 ] 128
             Item(Global): Logical Maximum, data= [ 0x7f ] 127
             Item(Global): Physical Minimum, data= [ 0x00 ] 0
             Item(Global): Physical Maximum, data= [ 0xff ] 255
             Item(Global): Report Size, data= [ 0x08 ] 8
             Item(Global): Report Count, data= [ 0x08 ] 8
             Item(Main  ): Input, data= [ 0x02 ] 2
                             Data Variable Absolute No_Wrap Linear
                             Preferred_State No_Null_Position Non_Volatile Bitfield
             Item(Local ): Usage, data= [ 0x05 ] 5
                             (null)
             Item(Local ): Usage, data= [ 0x06 ] 6
                             (null)
             Item(Global): Logical Minimum, data= [ 0x80 ] 128
             Item(Global): Logical Maximum, data= [ 0x7f ] 127
             Item(Global): Physical Minimum, data= [ 0x00 ] 0
             Item(Global): Physical Maximum, data= [ 0xff ] 255
             Item(Global): Report Size, data= [ 0x08 ] 8
             Item(Global): Report Count, data= [ 0x02 ] 2
             Item(Main  ): Output, data= [ 0x02 ] 2
                             Data Variable Absolute No_Wrap Linear
                             Preferred_State No_Null_Position Non_Volatile Bitfield
             Item(Main  ): End Collection, data=none
             Item(Main  ): End Collection, data=none
       Endpoint Descriptor:
         bLength                 7
         bDescriptorType         5
         bEndpointAddress     0x81  EP 1 IN
         bmAttributes            3
           Transfer Type            Interrupt
           Synch Type               None
           Usage Type               Data
         wMaxPacketSize     0x0008  1x 8 bytes
         bInterval              10
 Device Status:     0x0002
   (Bus Powered)
   Remote Wakeup Enabled
```
