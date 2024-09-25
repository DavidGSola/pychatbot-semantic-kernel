from typing import Annotated
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class SupermarketPlugin:
    @kernel_function(name="list_supermakets", description="List all supermarkets around the user")
    async def list_supermakets(
        self
    ) -> Annotated[list[str], "List of supermarkets around the user"]:
        "List all supermarkets around the user"
        
        return ["Mercadona", "Carrefour", "Coviran"]