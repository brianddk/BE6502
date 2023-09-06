# ref: https://falstad.com/circuit/circuitjs.html

def units(a, b, label):
    if a*b >= 1_000_000:
        prefix = "K"
        scale = 1/1000
    elif a*b <= 1/1_000_000:
        prefix = "μ"
        scale = 1_000_000
    elif a*b < 1:
        prefix = "m"
        scale = 1000
    else:
        prefix = ""
        scale = 1
    return (a*scale, b*scale, prefix+label)

def display(R1):
    Vdd    = 4.35
    Vled_a = 2.1
    Vled_b = 1.8

    Ia = (Vdd - Vled_a)/R1
    Ra = Vled_a/Ia
    Pa = Vled_a*Ia

    Ib = (Vdd - Vled_b)/R1
    Rb = Vled_b/Ib
    Pb = Vled_b*Ib

    Ia, Ib, I_label = units(Ia, Ib, "A")
    Ra, Rb, R_label = units(Ra, Rb, "Ω")
    Pa, Pb, P_label = units(Pa, Pb, "W")
    _,  R1, _label  = units(R1, R1, "Ω")

    print(f"\nFor a curcuit with a {R1:.0f}{_label} resistor:")
    print(f"  Led current from {Ia:.1f}{I_label} to {Ib:.1f}{I_label}")
    print(f"  Led resistance from {Ra:.1f}{R_label} to {Rb:.1f}{R_label}")
    print(f"  Led power from {Pa:.1f}{P_label} to {Pb:.1f}{P_label}")

if __name__ == "__main__":
    Ioh_max = 100 / 1000 # 100ma -> 0.1A
    Voh     = 1.5        # V
    P_max   = Ioh_max * Voh
    I_5v    = P_max / 5

    print(f"Max pin current = {I_5v * 1000:.1f}mA @ 5v")
    for R1 in [31, 220, 1000, 8000]:
        display(R1)

# For a curcuit with a 31Ω resistor:       
#   Current from 72.6mI to 82.3mI          
#   Led resistance from 28.9Ω to 21.9Ω     
#   Led power from 152.4mW to 148.1mW      
#                                          
# For a curcuit with a 220Ω resistor:      
#   Current from 10.2mI to 11.6mI          
#   Led resistance from 205.3Ω to 155.3Ω   
#   Led power from 21.5mW to 20.9mW        
#                                          
# For a curcuit with a 1KΩ resistor:       
#   Current from 2.2mI to 2.5mI            
#   Led resistance from 933.3Ω to 705.9Ω   
#   Led power from 4.7mW to 4.6mW          
#                                          
# For a curcuit with a 8KΩ resistor:       
#   Current from 281.2μI to 318.7μI        
#   Led resistance from 7.5KΩ to 5.6KΩ     
#   Led power from 590.6μW to 573.7μW      
