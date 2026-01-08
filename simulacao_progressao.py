import random
import math

# =========================
# CONFIGURAÇÕES PRINCIPAIS
# =========================

DIAS_SIMULADOS = 30

ENERGIA_MAX = 8
REGEN_MINUTOS = 15
PRIMEIRA_REGEN_MINUTOS = 5

SESSOES_POR_DIA = 4
TEMPO_SEM_ENERGIA_MIN = 6  # quanto tempo ele fica ativo sem energia

# Economia
CUSTO_BASE_VILA = 1000
CRESCIMENTO_VILA = 1.65

ESTAGIOS_POR_CONSTRUCAO = 4
CONSTRUCOES_POR_VILA = 5

EV_CARTINHA = 0.10  # 10% do custo do próximo estágio

# Pity
PITY_X = 10
RARAS_BASE = 2
RARAS_COM_PITY = 3


# =========================
# ESTADO DO JOGADOR
# =========================

energia = ENERGIA_MAX
moedas = 0
vila_atual = 1
estagio_atual = 0
tentativas_sem_raro = 0

tempo_minutos = 0


# =========================
# FUNÇÕES
# =========================

def custo_vila(vila):
    return CUSTO_BASE_VILA * (CRESCIMENTO_VILA ** (vila - 1))

def custo_estagio(vila):
    return custo_vila(vila) / (CONSTRUCOES_POR_VILA * ESTAGIOS_POR_CONSTRUCAO)

def gerar_cartinha(vila):
    global tentativas_sem_raro

    raras = RARAS_COM_PITY if tentativas_sem_raro >= PITY_X else RARAS_BASE
    total_cartas = 20

    cartas = (
        ["moeda_baixa"] * (9 - (raras - RARAS_BASE)) +
        ["moeda_media"] * 5 +
        ["comum"] * 3 +
        ["raro"] * raras +
        ["jackpot"]
    )

    resultado = random.choice(cartas)

    if resultado == "raro":
        tentativas_sem_raro = 0
    else:
        tentativas_sem_raro += 1

    ganho = 0

    if resultado == "moeda_baixa":
        ganho = custo_estagio(vila) * EV_CARTINHA * 0.5
    elif resultado == "moeda_media":
        ganho = custo_estagio(vila) * EV_CARTINHA * 1.2
    elif resultado == "jackpot":
        ganho = custo_estagio(vila) * EV_CARTINHA * 30
    else:
        ganho = 0  # itens não viram moeda direta

    return ganho


# =========================
# SIMULAÇÃO
# =========================

for dia in range(1, DIAS_SIMULADOS + 1):
    for sessao in range(SESSOES_POR_DIA):

        # Usa energia
        while energia > 0:
            energia -= 1
            moedas += gerar_cartinha(vila_atual)

        # Tempo ativo sem energia
        tempo_minutos += TEMPO_SEM_ENERGIA_MIN

        # Primeira regeneração rápida
        energia += tempo_minutos // PRIMEIRA_REGEN_MINUTOS
        tempo_minutos %= PRIMEIRA_REGEN_MINUTOS

        if energia > ENERGIA_MAX:
            energia = ENERGIA_MAX

        # Regeneração normal
        energia += tempo_minutos // REGEN_MINUTOS
        tempo_minutos %= REGEN_MINUTOS

        if energia > ENERGIA_MAX:
            energia = ENERGIA_MAX

        # Construção
        while moedas >= custo_estagio(vila_atual):
            moedas -= custo_estagio(vila_atual)
            estagio_atual += 1

            if estagio_atual >= (CONSTRUCOES_POR_VILA * ESTAGIOS_POR_CONSTRUCAO):
                vila_atual += 1
                estagio_atual = 0
                break

    print(f"Dia {dia}: Vila {vila_atual}, Estágio {estagio_atual}, Moedas {int(moedas)}")

print("\nRESULTADO FINAL")
print(f"Vila alcançada: {vila_atual}")
