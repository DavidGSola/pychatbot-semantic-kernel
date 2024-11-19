from typing import Annotated
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class SupermarketPlugin:
    
    @kernel_function(name="get_user_city", description="Get user city")
    async def get_user_city(
        self,
    ) -> Annotated[str, "User city"]:
        return 'Motril'
    
    @kernel_function(name="list_supermakets_on_city", description="List supermarkets with their categories on a city")
    async def list_supermakets(
        self,
        city: Annotated[str, "City name for the supermarkets"],
        number_of_supermarkets: Annotated[int, "Number of markets to be returned"]
    ) -> Annotated[list[{str, str}], "List of supermarkets and categories on a city"]:
        "List supermarkets with their categories on a city"
        
        if city.casefold() == 'Motril'.casefold():
            return [
                {"Coviran", "Meat & Poultry"},
                {"Lupi", "Hairdresser"},
                {"Perandres", "Fruits & Vegetables"},
                {"McMickey", "Luxury restaurant"},
                {"Carnicas Paquito", "Seafood"},
                {"Fresas", "Sweets"}
            ][:number_of_supermarkets]
        else:       
            return [
                {"Derby Market", "Meat"},
                {"Roadrunner Food Bank", "Fruit"},
                {"Jubilee Foods", "Vegetables"},
                {"Fry's Food Store", "Fish"},
                {"A & J Select Market", "Sweets"},
                {"Parsons Food", "Other"}
            ][:number_of_supermarkets]