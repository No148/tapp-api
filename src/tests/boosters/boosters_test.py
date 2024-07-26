from config import BOOSTERS


def test_purchase_boosters(client, user_before):
    purchasable_booster_keys = [list(item.keys())[0] for item in BOOSTERS['purchasable']]
    booster_price_accumulator = 0

    for purchasable_booster_key in purchasable_booster_keys:
        data = {
            "user_id": user_before["id"],
            "boost": purchasable_booster_key,
            "current_level": user_before["boosters"][purchasable_booster_key]["current_level"],
            "next_level": user_before["boosters"][purchasable_booster_key]["next_level"],
            "next_level_price": user_before["boosters"][purchasable_booster_key]["next_level_price"],
        }

        user_current_points = user_before["points"]
        booster_price = user_before["boosters"][purchasable_booster_key]["next_level_price"]
        booster_price_accumulator = booster_price_accumulator + booster_price
        
        if user_current_points > booster_price:
            response = client.post(f"api/v1/boosters/purchase", json=data)
            
            assert response.status_code == 200

            user_after = response.json()
            
            assert user_before["points"] - booster_price_accumulator == user_after["points"]
            assert user_before["boosters"][purchasable_booster_key]["next_level"] == user_after["boosters"][purchasable_booster_key]["current_level"]