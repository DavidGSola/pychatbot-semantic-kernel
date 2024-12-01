import requests

from typing import Annotated
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from typing import TypedDict

class BookModel(TypedDict):
    author: str
    title: str
    first_sentence: str

class BookRepositoryPlugin:

    @kernel_function(name='get_books_from_user_query', description='Call to search for books. The response includes the title, author and first sentence of the book.') 
    async def get_books_from_user_query(
        self,
        user_query: Annotated[str, 'User query. No more than 5 words.'],
    ) -> Annotated[list[BookModel], 'List of books']:    
        url = 'https://openlibrary.org/search.json'  
        params = {  
            'q': user_query,  
            'fields': 'key,title,author_name,first_sentence',  
            'limit': 5  
        }  

        response = requests.get(url, params=params)  
        response.raise_for_status()
        
        data = response.json()  
        books = []  
        
        for doc in data['docs']:  
            book = BookModel(  
                author=doc['author_name'][0],  
                title=doc['title'],  
                first_sentence='\n'.join(doc['first_sentence']) if 'first_sentence' in doc and doc['first_sentence'] else ""  
            )  
            books.append(book)  
        
        return books 