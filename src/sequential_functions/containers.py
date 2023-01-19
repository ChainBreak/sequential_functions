from threading import Thread
from multiprocessing import Pool
import types

class Compose():
    def __init__(self, *functions):
        self.function_list = functions

    def __call__(self, generator):

        for function in self.function_list:
            if isinstance(function, Compose):
                generator = function(generator)
            else:
                generator = self.wrap_function_in_generator(function,generator)

        return generator

    def wrap_function_in_generator(self,function, generator):
        for item in generator:

            result_item = function(item)

            # Functions can return item or generators that yield items
            if isinstance(result_item, types.GeneratorType):
                yield from result_item
            else:
                yield result_item
      
class MultiProcess(Compose):

    def __init__(self,*functions, num_workers=0):
        super().__init__(*functions)
        self.num_workers = num_workers


    def __call__(self,generator):

        with Pool(self.num_workers) as pool:
            for collated_items in pool.imap(self.worker_function, generator):
                for item in collated_items:
                    yield item

    def worker_function(self,item):

        # Wrap single item in generator for passing to the function chain
        def generator():
            yield item

        # Call the parent Compose class
        output_generator = super().__call__( generator() )

        # Collate all items incase there are more outputs than inputs
        collated_items = list(output_generator)
    
        return collated_items