vlan = int(input("Ingrese el número de VLAN: "))

if 1 <= vlan <= 1005:
    print("La VLAN corresponde al rango normal.")
elif 1006 <= vlan <= 4094:
    print("La VLAN corresponde al rango extendido.")
else:
    print("El número de VLAN no es válido.")  
