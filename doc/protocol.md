| Byte    | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| Example | 02 | 00 | 00 | 01 | 40 | 00 | AA | AA | 82 | 00 | 00 | 02 | FA | FA | FA | FA |

1. Byte: Bit 0 (Vorzeichen): 0 -> plus
1 -> minus
Bit 1, 2 (Dezimalpunkt (DP)):
0 0 -> NODP
0 1 -> LSD
1 0 -> MDP
1 1 -> MSD
Bit 5, 4, 3 (Modell):
0 0 0 -> M-3890D
Bit 6, 7 (Kanal):
0 0 -> MAIN
0 1 -> Sub1
1 0 -> Sub2
- - -> not used

2. Byte: Bit 7, 6, 5, 4 (Funktion)
0 0 0 0 -> DC V 0
0 0 0 1 -> AC V 1
0 0 1 0 -> Widerstand 2
0 0 1 1 -> DC uA 3
0 1 0 0 -> DC mA 4
0 1 0 1 -> DC A 5
0 1 1 0 -> AC uA 6
0 1 1 1 -> AC mA 7
1 0 0 0 -> AC A 8
1 0 0 1 -> Frequenz 9
1 0 1 0 -> Kapazität 10
1 0 1 1 -> Signal ausg. 11
- - - -
1 1 1 0 -> etc 14

Bit 3, 2, 1, 0 (Bereich DC V oder AC V):
0 0 0 0 -> mv 0
0 0 0 1 -> V 1

Bit 3, 2, 1, 0 (Bereich Widerstand):
0 0 0 0 -> Ohm 0
0 0 0 1 -> kOhm 1
0 0 1 0 -> MOhm 2

Bit 3, 2, 1, 0 (Bereich DC uA oder AC uA):
0 0 0 0 -> uA 0
0 0 0 1 -> mA 1

Bit 3, 2, 1, 0 (Bereich DC mA oder AC mA):
0 0 0 0 -> mA 0

Bit 3, 2, 1, 0 (Bereich DC A oder AC A):
0 0 0 0 -> A 0


Bit 3, 2, 1, 0 (Frequenz):
0 0 0 0 -> kHz 0
0 0 0 1 -> mHz 1

Bit 3, 2, 1, 0 (Kapazität):
0 0 0 0 -> nF 0
0 0 0 1 -> uF 1

Bit 3, 2, 1, 0 (etc):
0 0 0 0 -> Durchgang 0
0 0 0 1 -> Diode 1
0 0 1 0 -> hFE 2
0 0 1 1 -> Temperatur 3
0 1 0 0 -> Logik 4
0 1 0 1 -> EF 5
0 1 1 0 -> dB 6

3. Byte und 4. Byte (MAIN):
Byte 3: Bit 7, 6, 5, 4 -> first (1st) digit
Bit 3, 2, 1, 0 -> second (2nd) digit
Byte 4: Bit 7, 6, 5, 4 -> third (3rd) digit
Bit 3, 2, 1, 0 -> forth (4th) digit

digit 1, 2, 3, 4 (<10): 0 bis 9 <- Zahlenwert
digit 2, 3 = "rd" <- Logic range "rdy"
digit 2, 3 = "Lo" <- Logic range "Lo"
digit 2, 3 = "Hi" <- Logic range "Hi"
digit 4 = "-" <- Logic range "-----"

5. Byte (Sub1):
Bit 0: 0 -> plus
1 -> minus

Bit 2, 1 (DP):
0 0 -> NODP
0 1 -> LSD
1 0 -> MDP
1 1 -> MSD

Bit 5, 4, 3 (Model):
0 0 0 -> M3890D

Bit 7, 6 (Kanal):
0 0 -> Main
0 1 -> Sub1
1 0 -> Sub2
- - not used

6. Byte (Sub1):

Bit 7, 6, 5, 4 (Funktion): Display unit
0 0 0 0 -> DC V no unit
0 0 0 1 -> AC V dB
0 0 1 0 -> Widerstand no unit
0 0 1 1 -> DC uA no unit
0 1 0 0 -> DC mA no unit
0 1 0 1 -> DC A no unit
0 1 1 0 -> AC uA no unit
0 1 1 1 -> AC mA no unit
1 0 0 0 -> AC A no unit
1 0 0 1 -> Frequenz no unit
1 0 1 0 -> Kapazität no unit
1 0 1 1 -> Signal ausg. no unint
- - - - - -
1 1 1 0 -> etc no unit

7. Byte und 8. Byte (Sub 1):
Byte 7: Bit 7, 6, 5, 4 -> first (1st) digit
Bit 3, 2, 1, 0 -> second (2nd) digit
Byte 8: Bit 7, 6, 5, 4 -> third (3rd) digit
Bit 3, 2, 1, 0 -> forth (4th) digit

digit 1, 2, 3, 4 (<10): 0 bis 9 <- Zahlenwert
digit 1, 2, 3, 4 (<10)= " ": no display
digit 1, 2, 3, 4 (<10)= "OL": Overflow

9. Byte (Sub 2):
Bit 0: 0 -> plus
1 -> minus

Bit 1, 2 (Dezimalpunkt (DP)):
0 0 -> NODP
0 1 -> LSD
1 0 -> MDP
1 1 -> MSD
Bit 5, 4, 3 (Modell):
0 0 0 -> M-3890D
Bit 6, 7 (Kanal):
0 0 -> MAIN
0 1 -> Sub1
1 0 -> Sub2
- - -> not used

10. Byte (Sub 2):
Bit 7, 6, 5, 4 (Funktion): Display unit
0 0 0 0 -> DC V no unit
0 0 0 1 -> AC V dB
0 0 1 0 -> Widerstand no unit
0 0 1 1 -> DC uA no unit
0 1 0 0 -> DC mA no unit
0 1 0 1 -> DC A no unit
0 1 1 0 -> AC uA no unit
0 1 1 1 -> AC mA no unit
1 0 0 0 -> AC A no unit
1 0 0 1 -> Frequenz no unit
1 0 1 0 -> Kapazität no unit
1 0 1 1 -> Signal ausg. no unint
- - - - - -
1 1 1 0 -> etc no unit

Bit 3, 2, 1, 0 (Range): Display Unit
0 0 1 1 -> Temperatur F
0 1 0 0 -> Logik V
1 0 1 1 -> Signal Out V
