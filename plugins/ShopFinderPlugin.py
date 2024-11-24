from typing import Annotated
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class ShopFinderPlugin:
    
    @kernel_function(name="get_user_city", description="Get user city")
    async def get_user_city(
        self,
    ) -> Annotated[str, "User city"]:
        return 'Springfield'
    
    @kernel_function(name="list_shops_on_city", description="List shops on a city")
    async def list_shops(
        self,
        city: Annotated[str, "City name"],
        number_of_markets: Annotated[int, "Number of shops to be returned"]
    ) -> Annotated[list[{str, str}], "List of shops on a city"]:
        "List shops on a city"
        
        if city.casefold() == 'Springfield'.casefold():
            return [
                {"The Butcher's Block", "Meat & Poultry"},
                {"Brew Arsenal", "Coffee Equipment & Tools"},
                {"Bean Vault", "Specialty Coffee Beans"},
                {"MeanMarkt", "Consumer Electronics & Tools"},
                {"Pearl's Fresh Catch", "Seafood"},
                {"Barista Box", "Training & Education"},
                {"Sweet & Steam", "Coffee Shop"}
            ][:number_of_markets]
        else:       
            return [
                {"Prime & Proper", "Meat & Poultry"},
                {"The Copper Press", "Coffee Equipment & Tools"},
                {"Roasted Roots", "Specialty Coffee Beans"},
                {"TechForge", "Consumer Electronics & Tools"},
                {"Tides & Tales", "Seafood"},
                {"Grounds Academy", "Training & Education"},
                {"Crema & Co.", "Coffee Shop"}
            ][:number_of_markets]