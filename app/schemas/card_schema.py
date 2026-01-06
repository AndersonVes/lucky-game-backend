from pydantic import BaseModel

class CardReward(BaseModel):
    type: str
    amount: int | None = None # quantidade de grana

    buff: str | None = None # tipo de buff
    buff_duration_sec: int | None = None # duração do buff em segundos

    item_slug: str | None = None # referencia a tabela de itens

class Card(BaseModel):
    id_slug: str # coin_low, coin_medium, jackpot, boost_xp_small, rare_item, common_item...
    category: str
    image_url: str
    rarity: float
    draw_weight: float
    reward: CardReward