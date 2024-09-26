from typing import Annotated
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class SupermarketPlugin:
    @kernel_function(name="list_supermakets", description="List supermarkets with their categories")
    async def list_supermakets(
        self
    ) -> Annotated[list[{str, str}], "List of supermarkets and categories"]:
        "List supermarkets with their categories"
        
        return [
            {"Derby Market", "Meat"},
            {"Roadrunner Food Bank", "Fruit"},
            {"Jubilee Foods", "Vegetables"},
            {"Fry's Food Store", "Fish"},
            {"A & J Select Market", "Sweets"},
            {"Parsons Food", "Other"}
        ]