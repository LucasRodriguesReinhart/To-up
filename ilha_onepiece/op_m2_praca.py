# op_m2_praca.py - zona "plaza" do M2 (Ilha 5 ONE PIECE / WANO): FAIXA SUL DA PRACA + emblema rebaixado + borda da
# chegada (arrimo, mureta, toro, estandartes) + piso PROVISORIO do resto da praca. O codigo mora no op_m2_trecho
# (build_praca); este arquivo so existe porque o build_op chama mod.build() por zona.
import op_m2_trecho as T


def build():
    T.build_praca()
