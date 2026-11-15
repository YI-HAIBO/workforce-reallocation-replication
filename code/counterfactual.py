# -*- coding: utf-8 -*-
"""Model-based policy counterfactual: how gamma_M responds to institutional capacity (Prop 4)."""
# Accounting baseline (verified): s_M0*dN = 2.34, dL_M = 5.66, gamma = 0.586
sN = 2.34
dL = 5.66
gamma = 1 - sN/dL
print(f"Baseline: dL_M={dL}, gamma_M={gamma:.3f} (paper 0.586)")

print("\n=== Counterfactual: raise institutional capacity -> reinstatement channel recovers more ===")
print(f"{'extra reinstated (M)':<24}{'new dL_M':<12}{'new gamma':<12}{'residual 1-gamma':<18}")
for extra in [0.25, 0.5, 0.75, 1.0, 1.5]:
    dLp = dL + extra
    g = 1 - sN/dLp
    print(f"{extra:<24}{dLp:<12.2f}{g:<12.3f}{1-g:<18.3f}")

print("\n=== Skill-upgrade share under counterfactual ===")
# Baseline: dH=4.53 of which skill=3.822 (84%), pool+comp=0.712, residual qty=1.13
dH = 4.53
skill_base = 3.822
print(f"Baseline skill share of dH = {skill_base/dH*100:.1f}%")
# If the extra reinstated are at the higher tier, dH rises by extra
for extra in [0.5, 1.0]:
    dHp = dH + extra
    print(f"extra={extra}M -> dH'={dHp:.2f}, skill share'={skill_base/dHp*100:.1f}%")

print("\n=== Prop 4 calibration: gamma as function of I (concave rho) ===")
import math
# rho(I)=1-exp(-psi*I), B[nu+rho-1]=dL at I_China=2.07
psi = 0.5
def rho(I): return 1 - math.exp(-psi*I)
# pick nu so that at I=2.07, dL=5.66 with B=23.1 (illustrative displacement base)
B = 23.1
I_china = 2.07
nu = dL/B - rho(I_china) + 1
print(f"calibrated nu={nu:.4f} (so dL(I_china)=5.66)")
for I in [1.0, 2.07, 2.5, 3.0, 3.5, 4.0, 4.46]:
    dLi = B*(nu + rho(I) - 1)
    g = 1 - sN/dLi
    print(f"  I={I:<5} rho={rho(I):.3f} dL_M={dLi:6.2f} gamma={g:.3f}")
